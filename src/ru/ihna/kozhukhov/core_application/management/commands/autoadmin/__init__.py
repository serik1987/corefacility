import signal
import time
import logging
from argparse import ArgumentParser
from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand, CommandError
from django.utils import timezone
from django.utils.translation import gettext as _

from ru.ihna.kozhukhov.core_application.entity.entity_sets.log_set import LogSet
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import DeserializationException, \
    SecurityCheckFailedException, EntityNotFoundException
from ru.ihna.kozhukhov.core_application.models import PosixRequest
from ru.ihna.kozhukhov.core_application.models.enums import PosixRequestStatus, LogLevel
from ru.ihna.kozhukhov.core_application.utils import mail
from .auto_admin_object import AutoAdminObject
from .utils import deserialize_all_args, check_allowed_ip


class Command(BaseCommand):
    """
    Working with automatic administration requests.

    When you add users, groups or projects under PartServerConfiguration or FullServerConfiguration, the gunicorn
    worker process can't update Linux users and groups database because it doesn't run under the root. Instead of
    it, such a process adds so called 'posix request' to the core_application_posixrequest table in the database.
    """

    action_list = {
        "list": "View all POSIX requests",
        "detail": "View detailed information about the POSIX request with a given ID",
        "delete": "Removes the POSIX request with a given ID",
        "confirm": "Confirmation of the POSIX request (for part server configuration only)"
    }

    no_id_actions = ['list', '_loop']

    request_list_headers = {
        'id': "ID",
        'initialization_date': "Request date",
        'action_class': "Action class",
        'action_method': "Action method",
        'status': "Action status",
    }

    sleep_interval = 60.0
    """ Defines the sleep between two consecutive iterations """

    default_execution_interval = timedelta(minutes=10)
    """ Default value of the execution interval given that we have FullServerConfiguration """

    execution_interval = None
    """ How much time the process must be in status CONFIRMED until the autoadmin daemon executes it. """

    _action_classes = dict()

    _is_terminated = None
    """ True of the command has been terminated by the SIGTERM, SIGHUP, SIGQUIT or SIGINT loops, False otherwise """

    _is_terminable = True
    """
        True if SIGINT, SIGHUP, SIGQUIT and SIGTERM can terminate the command immediately
        False if they must wait until the command checks _is_terminated property being True
    """

    logger = None
    """ Standard corefacility logger """

    _log = None
    """ The log associated with a given security check issue. """

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        """
        Initialize the command.
        Please, not that in multi-thread execution the program must be constructed only from the main thread.

        :param stdout: the standard output stream to write
        :param stderr: the standard error stream to write
        :param no_color: Disable colorization of the output
        :param force_color: Force colorization of the output
        """
        super().__init__(stdout, stderr, no_color, force_color)
        if settings.CORE_UNIX_ADMINISTRATION:
            self.execution_interval = self.default_execution_interval
        elif settings.CORE_SUGGEST_ADMINISTRATION:
            self.execution_interval = timedelta()
        else:
            raise ImproperlyConfigured("Unrecognized configuration profile")
        for signal_number in (signal.SIGINT, signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT):
            signal.signal(signal_number, self.interrupt)
        self.logger = logging.getLogger("django.corefacility.log")

    def interrupt(self, signal_number, execution_frame):
        """
        Interrupts the daemon execution by the loop when it receives some terminating signal.

        :param signal_number: number of a signal that invoked this function
        :param execution_frame: the execution frame
        """
        if self._is_terminable:
            raise KeyboardInterrupt("The process has been terminated by the user")
        else:
            self._is_terminated = True

    def add_arguments(self, parser: ArgumentParser):
        """
        Adds specific command line arguments to the parser
        """

        help_text = "One of the following actions to do with POSIX request list: " + \
            "; ".join(["%s - %s" % (key, value) for key, value in self.action_list.items()]) + \
            ("If no action is specified, the command will be run in daemonized mode (i.e., will execute statuses of "
             "the posix request in infinite loop")

        id_help_text = "ID of the POSIX request action to deal with (required for all actions except {0})"\
            .format(", ".join(self.no_id_actions))

        parser.add_argument('action',
                            nargs='?',
                            choices=self.action_list.keys(),
                            help=help_text,
                            )

        parser.add_argument('id',
                            nargs='?',
                            type=int,
                            help=id_help_text,
                            )

        parser.description = Command.__doc__

    def handle(self, *args, action=None, id=None, **kwargs):
        """
        Handles the CLI command.
        The method reads an action selected by the user and calls proper method

        :param args: additional positioned arguments from the command line
        :param action: an action selected by the user
        :param id: ID of the POSIX request to deal with
        :param kwargs: additional non-positioned arguments from the command line
        """
        if not (settings.CORE_UNIX_ADMINISTRATION or settings.CORE_SUGGEST_ADMINISTRATION):
            raise CommandError("The command doesn't make sense for this particular configuration type")
        if action is None:
            action = "_loop"
        method = getattr(self, action)
        if action in self.no_id_actions:
            if id is not None:
                raise CommandError("The action doesn't require POSIX request ID to be specified")
            method()
        else:
            if id is None:
                raise CommandError("The action requires POSIX request ID to be specified")
            method(id)

    def list(self):
        """
        Prints all corefacility requests
        """
        posix_request_info = self._get_posix_request_info()
        self._print_list(self.request_list_headers, posix_request_info)

    def detail(self, request_id):
        """
        Prints detailed information about a given corefacility request

        :param request_id: ID of the request to print information
        """
        request_model = self._get_posix_request(request_id)
        action = self._extract_action(request_model)
        try:
            action.call(request_model)
            method = getattr(action, request_model.method_name)
            command_list = "\n" + action.flush_command_buffer() + "\n"
            log = LogSet().get(request_model.log_id)
        except Exception as err:
            raise CommandError("Failed to extract an action from the request model: " + str(err))
        request_details = "%s %s" % (log.request_method, log.log_address)
        request_author = self._get_request_author(log)

        request_table = {
            "ID:": request_model.id,
            "Request date:": request_model.print_initialization_date(),
            "Action class:": action.__doc__.strip().split("\n")[0],
            "Action:": method.__doc__.strip().split("\n")[0],
            "Action status:": PosixRequestStatus(request_model.status).name.lower(),
            "IP address:": str(log.ip_address),
            "Request details:": request_details,
            "Request author:": request_author,
            "Execution commands:": command_list
        }
        column_min_width = [len(name) for name, _ in request_table.items()]
        column_width = max(column_min_width)
        request_table = {name.rjust(column_width): value for name, value in request_table.items()}
        request_table = ["%s %s" % item for item in request_table.items()]
        request_table = "\n".join(request_table) + "\n"

        self.stdout.write(request_table)

    def delete(self, request_id):
        """
        Removes the corefacility request from the request list. The request will be fully cancelled.

        :param request_id: ID of the POSIX request to remove
        """
        request_model = self._get_posix_request(request_id)
        request_model.delete()
        self.stdout.write("The POSIX request with ID=%d has been successfully deleted.\n" % request_id)

    def confirm(self, request_id):
        """
        Confirms the corefacility request from the request list. Does nothing for FullServerConfiguration
        """
        if not settings.CORE_SUGGEST_ADMINISTRATION:
            return
        try:
            posix_model = PosixRequest.objects.get(status=PosixRequestStatus.ANALYZED, id=request_id)
            posix_model.status = PosixRequestStatus.CONFIRMED
            posix_model.save()
            self.stdout.write("Request number %d has been confirmed." % request_id)
        except PosixRequest.DoesNotExist:
            raise CommandError("There is no request with ID=%d that waits for the confirmation" % request_id)

    def _loop(self):
        """
        Turns the autadmin command into the infinite loop. The loop can be terminated by the SIGTERM only.
        """
        self._is_terminated = False
        try:
            while True:
                self._is_terminable = False
                initialized_requests = list(PosixRequest.objects.filter(status=PosixRequestStatus.INITIALIZED))
                for request_model in initialized_requests:
                    self._analyze_posix_request(request_model)
                    if self._is_terminated:
                        break
                filter_time = timezone.now() - self.execution_interval
                confirmed_requests = list(
                    PosixRequest.objects.filter(
                        status=PosixRequestStatus.CONFIRMED,
                        initialization_date__lt=filter_time,
                    )
                )
                for request_model in confirmed_requests:
                    self._execute_posix_request(request_model)
                    if self._is_terminated:
                        break
                if self._is_terminated:
                    break
                self._is_terminable = True
                time.sleep(self.sleep_interval)
        except KeyboardInterrupt:
            pass

    def _get_posix_request_info(self):
        """
        Reveals information about POSIX request and represents it in the form of Python dictionary

        :return: a list containing dictionaries related to the POSIX request list
        """
        posix_request_info = []
        # noinspection PyUnresolvedReferences
        for posix_request_model in PosixRequest.objects.all():
            try:
                action_class = self._get_action_class(posix_request_model)
                action_class_description = action_class.__doc__.strip().split('\n')[0]
            except Exception as err:
                action_class = None
                action_class_description = str(err)
            try:
                action_method = getattr(action_class, posix_request_model.method_name)
                action_method_description = action_method.__doc__.strip().split('\n')[0]
            except Exception as err:
                action_method_description = str(err)
            status = PosixRequestStatus(posix_request_model.status).name.lower()
            posix_request_info.append({
                'id': str(posix_request_model.id),
                'initialization_date': posix_request_model.print_initialization_date(),
                'action_class': action_class_description,
                'action_method': action_method_description,
                'status': status,
            })
        return posix_request_info

    def _get_action_class(self, action_model):
        """
        Recovers the action class from the model info.

        :param action_model: the action model to be used for recovery of the action class
        """
        try:
            return self._action_classes[action_model.action_class]
        except KeyError:
            module_name, class_name = action_model.action_class.rsplit('.', 1)
            action_module = import_module(module_name)
            action_class = getattr(action_module, class_name)
            return action_class

    def _print_list(self, request_list_headers, posix_request_info):
        """
        Prints the list as some kind of table. Each argument is a dictionary like column ID => column value

        :param request_list_headers: Headers column
        :param posix_request_info: list of all rows
        """
        column_size = {column_id: [] for column_id in request_list_headers.keys()}
        for row in [request_list_headers, *posix_request_info]:
            for column_id, column_value in row.items():
                column_size[column_id].append(len(column_value))
        column_size = {column_id: max(column_sizes) for column_id, column_sizes in column_size.items()}

        request_list_headers = {
            column_id: cell_value.ljust(column_size[column_id])
            for column_id, cell_value in request_list_headers.items()
        }
        request_paddings = {
            column_id: '-'*column_size[column_id] for column_id in request_list_headers.keys()
        }
        posix_request_info = [
            {
                column_id: column_value.ljust(column_size[column_id])
                for column_id, column_value in single_request_info.items()
            }
            for single_request_info in posix_request_info
        ]

        request_list_headers = "|".join([" %s " % value for value in request_list_headers.values()])
        request_paddings = "+".join(["-%s-" % value for value in request_paddings.values()])
        posix_request_info = "\n".join(
            [
                "|".join(
                    [
                        " %s " % value
                        for value in single_request_info.values()
                    ]
                )
                for single_request_info in posix_request_info
            ]
        )

        posix_request_info = "\n" + "\n".join([request_list_headers, request_paddings, posix_request_info]) + "\n\n"
        self.stdout.write(posix_request_info)

    # noinspection PyUnresolvedReferences
    def _get_posix_request(self, request_id):
        """
        Finds the PosixRequest object in the database using its ID

        :param request_id: ID of the POSIX request object
        :return: the POSIX request object itself
        """
        try:
            request_model = PosixRequest.objects.get(pk=request_id)
        except PosixRequest.DoesNotExist:
            raise CommandError("The POSIX request with ID = %d was not found." % request_id)
        return request_model

    def _extract_action(self, request_model):
        """
        Extracts the AutoAdminObject previously stored to the database

        :param request_model: a Django model object that reflects the database table row storing the information
            about the AutoAdminObject instance
        :return: the AutoAdminObject instance itself
        """
        try:
            action_class = self._get_action_class(request_model)
            if not issubclass(action_class, AutoAdminObject):
                raise ValueError("The autoadmin can execute only AutoAdminObject instances.")
            action_args, action_kwargs = deserialize_all_args(request_model.action_arguments)
            action = action_class(*action_args, **action_kwargs)
        except Exception as error:
            raise DeserializationException(request_model, error)
        return action

    def _analyze_posix_request(self, request_model):
        """
        Put the request marks as INTIIALIZED, checks it for safety and moves it towards ANALYZED or CONFIRMED state.

        :param request_model: a request itself
        :return: None
        """
        try:
            action = self._security_check(request_model)
            self._mail_admins(request_model, action)
            if settings.CORE_UNIX_ADMINISTRATION:
                request_model.status = PosixRequestStatus.CONFIRMED
                self._log.add_record(
                    LogLevel.INFO,
                    _("The request is analyzed and will be launched within the period of {0}")
                    .format(str(self.execution_interval))
                )
            if settings.CORE_SUGGEST_ADMINISTRATION:
                request_model.status = PosixRequestStatus.ANALYZED
                self._log.add_record(
                    LogLevel.INFO,
                    _("The request is analyzed and awaits for the confirmation of the system administrator.")
                )
            request_model.save()
        except Exception as error:
            self.logger.error(str(error))
            if self._log is not None:
                self._log.add_record(LogLevel.ERROR, str(error))
            if isinstance(error, SecurityCheckFailedException):
                self._log.add_record(
                    LogLevel.INFO,
                    _("This is a crucial security error. We decided to permanently interrupt the executed action.")
                )
                request_model.delete()

    def _execute_posix_request(self, request_model):
        """
        Executes the request marked as CONFIRMED.

        :param request_model: a request itself
        :return: None
        """
        print("Executing request ", request_model.id, "...", end="")
        time.sleep(1)
        print("Done.")

    def _security_check(self, request_model):
        """
        Provides security check for the request. The security check implies the follo`wing steps:
        1. If POSIX request doesn't have related log, the security check fails.
        2. If request was made from the IP address which is not in the list of allowed IP addresses, the security
        check failed.
        3. The request model must be deserialized into action object that shall be instance of the AutoAdminObject.
            If not, the security check failed.
        4. A valid method must be attached to such an action. If failed, the security check has failed.
        5. If security check has failed, the program will be logged.

        :return: an instance of AutoAdminObject that contains an action to execute.
        """
        try:
            self._log = LogSet().get(request_model.log_id)
        except EntityNotFoundException:
            raise SecurityCheckFailedException("The associated POSIX request was not attached to the model.")
        if self._log.user is None:
            raise SecurityCheckFailedException("Anonymous users can't make POSIX requests.")
        if not check_allowed_ip(self._log.ip_address):
            raise SecurityCheckFailedException(
                _("The request was made from inappropriate IP address %s") % self._log.ip_address
            )
        try:
            action = self._extract_action(request_model)
        except DeserializationException as error:
            raise SecurityCheckFailedException(str(error))
        if not hasattr(action, request_model.method_name):
            raise SecurityCheckFailedException(
                "Method '%s' was not defined in related action object." % request_model.method_name
            )
        return action

    def _mail_admins(self, request_model, action):
        """
        Sends E-mail notification to the system administrators
        """
        action_method = getattr(action, request_model.method_name)
        action.call(request_model)
        command_list = action.flush_command_buffer()

        mail(
            template_prefix='core/action_request',
            context_data={
                'admin_name': settings.ADMIN_NAME,
                'action_id': request_model.id,
                'log_id': self._log.id,
                'request_date': request_model.print_initialization_date(),
                'action_class': action.__doc__.strip().split('\n')[0],
                'action_name': action_method.__doc__.strip().split('\n')[0],
                'ip': str(self._log.ip_address),
                'request_details': "%s %s" % (self._log.request_method, self._log.log_address),
                'request_author': self._get_request_author(),
                'command_list': command_list,
                'url_base': settings.URL_BASE,
                'is_suggest': settings.CORE_SUGGEST_ADMINISTRATION,
                'sleep_time': str(self.default_execution_interval),
            },
            subject=_("Request for the administrative task"),
            recipient=settings.ADMIN_EMAIL,
        )

    def _get_request_author(self, log=None):
        """
        Returns string representation of a user making the request

        :param log: log related to the request or None fi you are inside the _loop()
        :return: the user related to the request
        """
        if log is None:
            log = self._log
        if log.user.name is None and log.user.surname is None:
            request_author = log.user.login
        elif log.user.name is None or log.user.surname is None:
            request_author = "%s [%s]" % (log.user.name or log.user.surname, log.user.login)
        else:
            request_author = "%s %s [%s]" % (log.user.name, log.user.surname, log.user.login)
        return request_author
