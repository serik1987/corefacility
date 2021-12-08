from django.db import models


class ExternalAuthorizationSession(models.Model):
    """
    Stores information about all external authorization sessions.
    """
    authorization_module = models.ForeignKey("Module", on_delete=models.CASCADE, editable=False,
                                             help_text="The authorization module through which the authorization "
                                                       "is provided")
    session_key = models.CharField(max_length=256, editable=False,
                                   help_text="The session key is used to prove that external authorization system "
                                             "redirects the same user which actually types loging and password")
    session_key_expiry_date = models.DateTimeField(editable=False,
                                                   help_text="The session key is valid for approximately 1 hour")
