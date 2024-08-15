from django.db import models

from .enums.labjournal_field_type import LabjournalFieldType


class LabjournalParameterDescriptor(models.Model):
    """
    Describes custom parameters
    """

    category = models.ForeignKey(
        "LabjournalRecord",
        help_text="The parameter can be set only in given category or any of its descendant records." +
        "NULL for the root category",
        on_delete=models.CASCADE,
        null=True,
    )

    project = models.ForeignKey(
        "Project",
        help_text="The parameter identifier must be unique across the whole project. Also, when the parameter " +
        "belong to the root category this field shows which one it belongs to",
        on_delete=models.CASCADE,
        null=False,
    )

    identifier = models.SlugField(
        help_text="String identifier of the field (to be used in Matlab or Python)",
        max_length=256,
        null=False,
        db_index=True,
    )

    index = models.PositiveSmallIntegerField(
        help_text="Parameters with a higher index will be displaced below parameters with a lower index",
        null=False,
    )

    description = models.CharField(
        max_length=256,
        help_text="Short human-readable description of the field",
        null=False,
        blank=False,
    )

    type = models.CharField(
        max_length=1,
        help_text="Type for the parameter value",
        choices=LabjournalFieldType.choices,
        null=False,
        blank=False,
    )

    required = models.BooleanField(
        help_text="Whether the parameter is required",
    )

    default = models.CharField(
        max_length=256,
        help_text="Default value for the field or NULL if the field doesn't have default field",
        null=True,
    ),

    for_data_record = models.BooleanField(
        help_text="Applicable for the data records",
        null=False,
        blank=False,
        default=True,
    )

    for_service_record = models.BooleanField(
        help_text="Applicable for the service records",
        null=False,
        blank=False,
        default=True,
    )

    for_category_record = models.BooleanField(
        help_text="Applicable for the category records",
        null=False,
        blank=False,
        default=True,
    )

    units = models.CharField(
        help_text="Units for the field",
        max_length=32,
        null=True,
        blank=False,
    )

    class Meta:
        unique_together = [["project_id", "identifier"], ["category_id", "index"]]
        ordering = ("index",)
