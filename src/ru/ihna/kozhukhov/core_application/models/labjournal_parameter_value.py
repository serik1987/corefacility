from django.db import models


class LabjournalParameterValue(models.Model):
    """
    Represents a single parameter value
    """

    descriptor = models.ForeignKey(
        "LabjournalParameterDescriptor",
        on_delete=models.RESTRICT,
        help_text="descriptor that describes a given parameter",
        null=False,
    )

    record = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        help_text="Record this value relates to",
        null=False,
    )

    string_value = models.CharField(
        max_length=256,
        help_text="String or discrete value (if applicable)",
        null=True,
        db_index=True,
    )

    float_value = models.FloatField(
        help_text="Float or boolean value (if applicable)",
        null=True,
        db_index=True,
    )

    class Meta:
        unique_together = [["descriptor_id", "record_id"]]
