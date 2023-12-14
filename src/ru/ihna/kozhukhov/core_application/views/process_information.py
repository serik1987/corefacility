import subprocess

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ProcessInformation(APIView):
    """
    Retrieval information about processes.

    The information will be presented in an unordered way.
    """

    COMMAND = "ps aux"
    PROCESS_INFO_DESCRIPTION_ROW = 0
    INT_FIELDS = ['PID', 'VSZ', 'RSS']
    FIELD_TYPES = {
        'USER': str,
        'PID': int,
        '%CPU': float,
        '%MEM': float,
        'USZ': int,
        'RSS': int,
        'TTY': str,
        'STAT': str,
        'START': str,
        'TIME': str,
        'COMMAND': str,
    }

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Returns the list of all processes

        :param request: the request received from the HTTP client
        :param args: arguments revealed from parsing the request path
        :param kwargs: keyword arguments revealed from parsing the request path
        :return: the response to be sent to the client
        """
        process_table = subprocess.run(
            self.COMMAND.split(),
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            check=True
        )   \
            .stdout \
            .decode('utf-8')
        process_info_list = process_table.split('\n')
        field_list = process_info_list[self.PROCESS_INFO_DESCRIPTION_ROW].split()
        process_list = list()
        for process_info_string in process_info_list[self.PROCESS_INFO_DESCRIPTION_ROW+1:]:
            process_info = process_info_string.split()
            process = dict()
            for field_index, field_value in enumerate(process_info):
                try:
                    field_name = field_list[field_index]
                    if field_name in self.FIELD_TYPES:
                        process[field_name] = self.FIELD_TYPES[field_name](field_value)
                    else:
                        process[field_name] = field_value
                except IndexError:
                    process['COMMAND'] = "%s %s" % (process['COMMAND'], field_value)
            if 'PID' in process and process['COMMAND'] != self.COMMAND:
                process_list.append(process)
        return Response(process_list)
