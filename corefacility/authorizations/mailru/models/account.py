from django.db import models


class Account(models.Model):
    """
    Allows to attach mail.ru account to the corefacility account
    """
    email = models.EmailField(db_index=True, unique=True,
                              help_text="The user E-mail when he registered in the Mail.ru system")
    user = models.ForeignKey("core.User", on_delete=models.CASCADE, related_name="mailru_account",
                             help_text="corefacility user to which this account is attached")
