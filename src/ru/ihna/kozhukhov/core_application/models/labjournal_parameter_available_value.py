from django.db import models


class LabjournalParameterAvailableValue(models.Model):
    """
    List of all available values for a given parameter
    """

    descriptor = models.ForeignKey(
        "LabjournalParameterDescriptor",
        on_delete=models.CASCADE,
        help_text="Parameter which value is mentioned",
        null=False,
    )

    alias = models.SlugField(
        max_length=256,
        help_text="short string identifier of the value",
        null=False,
        db_index=True,
    )

    description = models.CharField(
        max_length=256,
        help_text="Human-readable value description",
        null=False,
    )

    class Meta:
        unique_together = [["descriptor_id", "alias"]]
