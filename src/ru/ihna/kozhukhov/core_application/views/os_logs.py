import os
import re

from dateutil import parser
from django.utils.timezone import is_aware, make_naive
from rest_framework.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ru.ihna.kozhukhov.core_application.exceptions.os_logs import NoLogDirectoryException


class OperatingSystemLogs(APIView):
    """
    Shows the user some of the requested logs from the rsyslog file
    """

    permission_classes = [IsAuthenticated]

    LOG_FOLDER = "/var/log/corefacility"
    DEFAULT_LOG_FILES = ["syslog", "auth.log"]
    VALID_FILENAME = re.compile(r'^[\w.,_\-;]+$')

    __log_files = None
    __log_data = None
    __host_list = None

    def get(self, request, *args, **kwargs):
        """
        Shows the user some of the requested logs from the rsyslog file

        :param request: the request received from the client application
        :param args: arguments revealed from the path
        :param kwargs: keyword arguments revealed from the path
        :return: the response to be sent to the client application
        """
        if not os.path.isdir(self.LOG_FOLDER):
            raise NoLogDirectoryException()
        self.__log_data = []
        self.__host_list = set()
        self.__log_files = []
        ordering = request.query_params.get('ordering', 'asc').lower()
        if ordering not in ('asc', 'desc'):
            raise ValidationError({'ordering': "Only 'asc' or 'desc' values are allowed"})
        reverse = ordering == 'desc'

        if 'files' in request.query_params:
            log_files = request.query_params['files'].split(',')
            log_files = filter(lambda filename: self.VALID_FILENAME.match(filename) is not None, log_files)
        else:
            log_files = self.DEFAULT_LOG_FILES

        for log_file in log_files:
            self.__read_log(log_file)
        self.__filter_log(request.query_params)
        self.__sort_log(reverse)
        self.__limit_log(request.query_params)

        response = Response({
            'log_files': self.DEFAULT_LOG_FILES,
            'host_list': list(self.__host_list),
            'log_data': self.__log_data,
        })

        self.__log_files = None
        self.__host_list = None
        self.__log_data = None

        return response

    def __read_log(self, log_file):
        """
        Reads the data from the log file

        :param log_file: the log file to process. You must point the relative path to the /var/log/corefacility folder
        """
        log_path = os.path.join(self.LOG_FOLDER, log_file)
        if not os.path.isfile(log_path):
            return
        self.__log_files.append(log_file)

        with open(log_path, 'r') as log_file:
            for log_info in log_file:
                log_info = log_info.strip().split()
                if len(log_info) == 0:
                    continue
                if log_info[0].find('<') != -1 and log_info[0].find('>') != -1:
                    log_info = log_info[1:]
                hostname_index = 1
                while hostname_index < len(log_info):
                    timestamp = ' '.join(log_info[:hostname_index])
                    try:
                        time = parser.parse(timestamp)
                    except parser.ParserError:
                        hostname_index -= 1
                        break
                    hostname_index += 1
                if hostname_index > len(log_info) - 1:
                    continue
                self.__log_data.append({
                    'time': time,
                    'hostname': log_info[hostname_index],
                    'message': ' '.join(log_info[hostname_index+1:])
                })
                self.__host_list.add(log_info[hostname_index])

    def __filter_log(self, filter_criteria):
        """
        Filters logs according to different criteria

        :param filter_criteria: a QueryDict object that represents different filtration criteria
        """
        if 'start' in filter_criteria:
            try:
                start = parser.parse(filter_criteria['start'])
                if is_aware(start):
                    start = make_naive(start)
            except parser.ParserError:
                raise ValidationError({'start': "Invalid date"})
            self.__log_data = filter(lambda log: log['time'] >= start, self.__log_data)

        if 'end' in filter_criteria:
            try:
                finish = parser.parse(filter_criteria['end'])
                if is_aware(finish):
                    finish = make_naive(finish)
            except parser.ParserError:
                raise ValidationError({'end': "Invalid date"})
            try:
                self.__log_data = filter(lambda log: log['time'] <= finish, self.__log_data)
            except TypeError:
                raise ValidationError({'end': "Invalid date"})

        if 'hostname' in filter_criteria:
            self.__log_data = filter(lambda log: log['hostname'] == filter_criteria['hostname'], self.__log_data)

        if 'q' in filter_criteria:
            template = re.compile(filter_criteria['q'])
            self.__log_data = filter(lambda log: template.search(log['message']) is not None, self.__log_data)

        try:
            self.__log_data = list(self.__log_data)
        except TypeError as error:
            raise ValidationError({
                "code": "bad_query_parameters",
                "detail": str(error),
            })

    def __sort_log(self, reverse):
        """
        Sorts logs in ascending or descending mode

        :param reverse: True to sort in descending mode, False otherwise
        """
        self.__log_data.sort(reverse=reverse, key=lambda log: log['time'])

    def __limit_log(self, limit_options):
        """
        Leaves only certain amount of logs

        :params limit_options: a QueryDict with the following keys:
            limit_start - from which element to start the output (default is 0)
            limit how many logs to output (default is all logs satisfying the filtration criteria)
        """
        try:
            start = int(limit_options.get('limit_start', 0))
        except ValueError:
            raise ValidationError({'limit_start': 'must be an integer'})
        if start < 0:
            raise ValidationError({'limit_start': 'must be positive or zero'})

        if 'limit' in limit_options:
            try:
                limit = int(limit_options['limit'])
            except ValueError:
                raise ValidationError({'limit': 'must be an integer'})
            if limit <= 0:
                raise ValidationError({'limit': 'must be positive'})
            self.__log_data = self.__log_data[start:(start + limit)]
        else:
            self.__log_data = self.__log_data[start:]
