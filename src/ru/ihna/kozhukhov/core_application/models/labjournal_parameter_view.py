from django.db import models


class LabjournalParameterView(models.Model):
    """
    Defines which parameter can be viewed by the user and in which order
    If the parameter was not mentioned in this table it must be shown
    """

    index = models.PositiveSmallIntegerField(
        help_text="Consequtive index for the field",
        null=False,
    )

    descriptor = models.ForeignKey(
        "LabjournalParameterDescriptor",
        on_delete=models.CASCADE,
        help_text="Descriptor for that parameter",
        null=False,
    )

    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        help_text="The related project",
        null=False,
    )

    category = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        help_text="Record where the parameter must be shown or hidden",
        null=True,
    )

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        help_text="User that must see this record",
        null=False,
    )

    class Meta:
        unique_together = [
            ["project_id", "category_id", "user_id", "descriptor_id"],
        ]
