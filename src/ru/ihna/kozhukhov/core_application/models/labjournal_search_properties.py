from django.db import models


class LabjournalSearchProperties(models.Model):
    """
    Allows to store search properties set by a given user in the database

    Absence of a certain row in this table means that the user did not set any filters
    (hence, all records will be shown)
    """

    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        help_text="Related project",
        null=True,
    )

    category = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        help_text="Category which search parameters are checked by the user",
        null=True,
    )

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        help_text="User that adjusted given filter properties",
        null=False,
    )

    properties = models.JSONField(
        help_text="Given search properties in JSON format",
        null=False,
        default=dict,
    )

    class Meta:
        unique_together=[["category_id", "user_id"]]
