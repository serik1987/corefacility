from django.db import models


class Account(models.Model):
    """
    Stores all attachments of the IHNA accounts to the corefacility accounts
    """
    email = models.EmailField(db_index=True, unique=True,
                              help_text="The user e-mail as typed for the IHNA personal page")
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="ihna_account",
                             help_text="The corefacility user to which ihna account is attached")
