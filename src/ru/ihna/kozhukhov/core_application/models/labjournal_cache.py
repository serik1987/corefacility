from django.db import models


class LabjournalCache(models.Model):
    """
    Stores dependent information that facilitates access to labjournal records
    """

    category = models.OneToOneField(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        primary_key=True,
        help_text="Category which cache is stored here",
        null=False,
    )

    path = models.CharField(
        max_length=256,
        help_text="Path to the record",
        null=False,
        db_index=True,
        unique=True
    )

    descriptors = models.JSONField(
        help_text="Descriptors related to a given directory as well as to all ascendent directories",
        null=True,
    )

    custom_parameters = models.JSONField(
        help_text="Default parameter values",
        null=True,
    )

    base_directory = models.CharField(
        max_length=256,
        help_text="Base directory for the containing record",
        null=True
    )
