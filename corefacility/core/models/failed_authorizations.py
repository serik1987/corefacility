from django.db import models


class FailedAuthorizations(models.Model):
    """
    Represents a table with failed authorizations
    """

    auth_time = models.DateTimeField(editable=False, db_index=True,
                                     help_text="Authorization time")
    ip = models.GenericIPAddressField(editable=False, null=False,
                                      help_text="The IP address defined")
    user = models.ForeignKey("User", editable=False, null=True, on_delete=models.SET_NULL,
                             help_text="The user that is trying to be authorized")
