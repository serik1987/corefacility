from django.db import models

from ....models import Authentication


class AuthorizationToken(models.Model):
    """
    Defines a storage place where all authorization tokens will be saved
    """
    access_token = models.CharField(max_length=256, editable=False,
                                    help_text="The authorization token that provides an access of the application "
                                              "to all Google facilities")
    expires_in = models.DateTimeField(editable=False,
                                      help_text="Date and time when authorization token expires")
    refresh_token = models.CharField(max_length=256, editable=False,
                                     help_text="This token will be used when authorization token expires")
    authentication = models.OneToOneField(Authentication, on_delete=models.CASCADE, null=True,
                                          help_text="Link to the authentication details",
                                          related_name="google_token")
