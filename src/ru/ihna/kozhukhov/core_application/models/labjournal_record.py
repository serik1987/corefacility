from django.db import models

from .enums.labjournal_record_type import LabjournalRecordType


class LabjournalRecord(models.Model):
    """
    Represents a single record in the laboratory journal stored in the database
    """

    parent_category = models.ForeignKey(
        "LabjournalRecord",
        null=True,
        help_text="Parent category or NULL if root",
        on_delete=models.RESTRICT,
    )

    project = models.ForeignKey(
        "Project",
        null=False,
        help_text="Related project",
        on_delete=models.CASCADE,
    )

    level = models.PositiveSmallIntegerField(
        null=False,
        help_text="Level of the root category is zero. Level of any other record is level of the category plus 1",
        db_index=True,
    )

    alias = models.SlugField(
        max_length=64,
        null=True,
        help_text="String ID for the record (not applicable for service records)"
    )

    datetime = models.DateTimeField(
        null=True,
        help_text="Date and time of the start of event",
        db_index=True,
    )

    type = models.CharField(
        null=False,
        choices=LabjournalRecordType.choices,
        max_length=1,
        help_text="The record type",
        db_index=True,
    )

    comments = models.TextField(
        null=True,
        help_text="Extra information",
    )

    name = models.CharField(
        null=True,
        help_text="Head of the service record (if applicable)",
        max_length=256,
        db_index=True,
    )

    finish_time = models.DateTimeField(
        null=True,
        help_text="Date and time of the last event within the category (if applicable)",
    )

    base_directory = models.CharField(
        null=True,
        max_length=256,
        help_text="Base directory for the category"
    )

    custom_parameters = models.JSONField(
        null=False,
        default=dict,
    )
