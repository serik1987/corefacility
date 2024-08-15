from django.db import models

from .enums.labjournal_hashtag_type import LabjournalHashtagType


class LabjournalHashtag(models.Model):
    """
    Stores information about record or file hashtags
    """

    description = models.CharField(
        max_length=64,
        help_text="Text containing in the hashtag",
        null=False,
        db_index=True,
    )

    project = models.ForeignKey(
        "Project",
        help_text="Project related to the hashtag",
        on_delete=models.CASCADE,
        null=False,
        db_index=True,
    )

    type = models.CharField(
        max_length=1,
        help_text="R for record hashtag, F for file hashtag",
        choices=LabjournalHashtagType.choices,
        null=False,
        db_index=True,
    )

    class Meta:
        unique_together = [
            ["project_id", "type", "description"]
        ]
