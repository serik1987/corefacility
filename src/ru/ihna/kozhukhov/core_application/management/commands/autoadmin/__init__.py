from argparse import ArgumentParser
from importlib import import_module

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from ru.ihna.kozhukhov.core_application.entity.entity_sets.log_set import LogSet
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import DeserializationException
from ru.ihna.kozhukhov.core_application.models import PosixRequest
from ru.ihna.kozhukhov.core_application.models.enums import PosixRequestStatus
from .auto_admin_object import AutoAdminObject
from .utils import deserialize_all_args


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

    no_id_actions = ['list']

    request_list_headers = {
        'id': "ID",
        'initialization_date': "Request date",
        'action_class': "Action class",
        'action_method': "Action method",
        'status': "Action status",
    }

    _action_classes = dict()

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
        if log.user.name is None and log.user.surname is None:
            request_author = log.user.login
        elif log.user.name is None or log.user.surname is None:
            request_author = "%s [%s]" % (log.user.name or log.user.surname, log.user.login)
        else:
            request_author = "%s %s [%s]" % (log.user.name, log.user.surname, log.user.login)

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
        print("Confirm POSIX action", request_id)

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
            raise DeserializationException(request_model.id, error)
        return action
