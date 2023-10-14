from django.db import models
from django.utils.timezone import make_naive

from .log import Log
from .enums import PosixRequestStatus


class PosixRequest(models.Model):
    """
    When the user tries to run an administrative privileged action from an API request, such an action can not be
    run immediately because python WSGI server doesn't run under root. To accomplish such an action the API request
    view must save the action parameters inside this model.

    A special crawler daemon being run under the root privileges will the information stored in this model and execute
    the requested command.
    """

    initialization_date = models.DateTimeField(editable=False, db_index=True, auto_now_add=True)
    action_class = models.CharField(editable=False, max_length=1024)
    action_arguments = models.JSONField(editable=False)
    method_name = models.CharField(editable=False, max_length=1024)
    method_arguments = models.JSONField(editable=False)
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=PosixRequestStatus.choices, default=PosixRequestStatus.INITIALIZED)

    def print_initialization_date(self):
        """
        Returns an initialization date as well-printed string

        :return: string containing the initialization date
        """
        return make_naive(self.initialization_date).strftime("%d.%m.%Y %H:%M:%S.%f")
