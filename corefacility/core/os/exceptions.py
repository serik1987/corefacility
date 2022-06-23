from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status


class SynchronicityError(Exception):
    """
    Raises in case of synchronicity problems
    """
    pass


class OsCommandFailedError(APIException):

    status = status.HTTP_400_BAD_REQUEST
    code = "posix_error"
    detail = None

    def __init__(self, detail):
        self.detail = detail


class OsConfigurationSuggestion(APIException):

    status = status.HTTP_400_BAD_REQUEST
    code = "action_required"
    detail = None

    MESSAGE = _("Please, login to the server using SSH, execute the commands listed below \n"
                "and press Continue to finish this action\n\n")

    def __init__(self, command_list):
        commands = []
        for command in command_list:
            commands.append(" ".join(command['args'][0]))
        self.detail = self.MESSAGE + "\n".join(commands)
