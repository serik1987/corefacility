from django.db import models


class Authentication(models.Model):
    """
    Stores the data responsible for checking and issuing the authentication tokens
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE, help_text="The authenticated user", editable=False)
    expiration_date = models.DateTimeField(help_text="Date and time until which the token is valid",
                                           editable=False)
    token_hash = models.CharField(max_length=256, editable=False,
                                  help_text="Hash code for the authentication token. The authentication token is"
                                            "needed for authenticating requests")
