from django.db import models


class LabjournalRootRecord(models.Model):
    """
    Represents the root category.
    A peculiarity of the root category is that it has very small fields
    """

    project = models.OneToOneField(
        "Project",
        null=False,
        on_delete=models.CASCADE,
        help_text="Related project",
        primary_key=True,
    )

    comments = models.TextField(
        null=True,
        help_text="Extra information",
    )

    base_directory = models.CharField(
        null=False,
        max_length=256,
        help_text="Base directory for the category"
    )
