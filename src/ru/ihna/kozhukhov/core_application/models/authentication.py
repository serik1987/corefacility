from django.db import models


class Authentication(models.Model):
    """
    Stores the data responsible for checking and issuing the authentication tokens
    """
    user = models.ForeignKey("User", on_delete=models.CASCADE, editable=False)
    expiration_date = models.DateTimeField()
    token_hash = models.CharField(max_length=256, editable=False)
