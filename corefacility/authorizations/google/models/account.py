from django.db import models


class Account(models.Model):
    """
    Stores information about all google accounts
    """
    user = models.OneToOneField("core.User", on_delete=models.CASCADE,
                                help_text="User to which this Google account is attached")
    email = models.EmailField(db_index=True,
                              help_text="The user e-mail address in the Google")
