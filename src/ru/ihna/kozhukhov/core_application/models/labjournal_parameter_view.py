from django.db import models


class LabjournalParameterView(models.Model):
    """
    Defines which parameter can be viewed by the user and in which order
    If the parameter was not mentioned in this table it must be shown
    """

    descriptor = models.ForeignKey(
        "LabjournalParameterDescriptor",
        on_delete=models.CASCADE,
        help_text="Descriptor for that parameter",
        null=False,
    )

    record = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        help_text="Record where the parameter must be shown or hidden",
        null=False,
    )

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        help_text="User that must see this record",
        null=False,
    )

    is_visible = models.BooleanField(
        help_text="True if the field must be visible; False otherwise",
        null=False,
    )

    index = models.PositiveSmallIntegerField(
        help_text="Consequtive index for the field",
        null=False,
    )

    class Meta:
        unique_together = [
            ["record_id", "user_id", "descriptor_id"],
            ["record_id", "user_id", "index"]
        ]
