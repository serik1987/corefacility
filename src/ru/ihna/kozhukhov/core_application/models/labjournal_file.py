from django.db import models


class LabjournalFile(models.Model):
    """
    Represents link to a given file
    """

    name = models.CharField(
        max_length=256,
        help_text="Name of the file (relatively to the base directory of the corresponding category)",
        null=False,
        db_index=True,
    )

    record = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.RESTRICT,
        help_text="ID of the record the file relates to",
        null=False,
    )

    class Meta:
        unique_together = [
            ['name', 'record_id']
        ]
