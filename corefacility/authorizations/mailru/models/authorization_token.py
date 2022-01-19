from django.db import models


class AuthorizationToken(models.Model):
    """
    Provides access to the mailru_authorizationtoken table
    """

    access_token = models.CharField(max_length=256, null=False, blank=False)
    expires_in = models.DateTimeField(null=False, blank=False)
    refresh_token = models.CharField(max_length=256, null=False, blank=False)
    authentication = models.OneToOneField("core.Authentication", on_delete=models.CASCADE,
                                          related_name="mailru_token")
