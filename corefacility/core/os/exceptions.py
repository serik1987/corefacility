from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status


class SynchronicityError(Exception):
    """
    Raises in case of synchronicity problems
    """
    pass


class OsCommandFailedError(APIException):

    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail):
        self.detail = {"code": "posix_error", "detail": detail}


class OsConfigurationSuggestion(APIException):

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "action_required"
    default_detail = None

    MESSAGE = _("Please, login to the server using SSH, execute the commands listed below \n"
                "and press Continue to finish this action\n\n")

    def __init__(self, command_list):
        commands = []
        for command in command_list:
            commands.append(" ".join(command['args'][0]))
        detail = self.MESSAGE + "\n".join(commands)
        self.detail = {"code": "action_required", "detail": detail}
