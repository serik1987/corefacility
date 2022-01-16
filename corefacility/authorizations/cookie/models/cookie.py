from django.db import models


class Cookie(models.Model):
    """
    Stores cookie tokens given an appropriate user.

    When some cookie is received from the remote client,
    this storage can be used to attach cookie to a given user
    """
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="cookie",
                             help_text="Actual corefacility user that have this cookie")
    token_hash = models.CharField(max_length=256,
                                  help_text="Token hash given to that user")
    expiration_date = models.DateTimeField(help_text="Cookie also have some short amount of life defined by a "
                                                     "the server system administrator")
