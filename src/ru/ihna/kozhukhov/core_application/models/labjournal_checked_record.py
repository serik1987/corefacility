from django.db import models


class LabjournalCheckedRecord(models.Model):
    """
    Contains information about whether the record is checked by the user or not

    No such information means that the record did not checked by a given user
    """

    record = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        help_text="ID of the record which check status is stored in a given row",
        null=False,
    )

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        help_text="ID of the user that checked or unchecked the record",
        null=False,
    )

    class Meta:
        unique_together = [["record_id", "user_id"]]
