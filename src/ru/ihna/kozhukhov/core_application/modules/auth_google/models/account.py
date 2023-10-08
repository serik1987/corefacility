from django.db import models

from ....models import User


class Account(models.Model):
    """
    Stores information about all google accounts
    """
    email = models.EmailField(db_index=True,
                              help_text="The user e-mail address in the Google")
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                help_text="User to which this Google account is attached")
