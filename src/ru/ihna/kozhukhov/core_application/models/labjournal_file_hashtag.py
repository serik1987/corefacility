from django.db import models


class LabjournalFileHashtag(models.Model):
    """
    Stores connection of file hashtags to files itself
    """

    hashtag = models.ForeignKey(
        "LabjournalHashtag",
        on_delete=models.CASCADE,
        null=False,
    )

    file = models.ForeignKey(
        "LabjournalFile",
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        unique_together = [
            ['hashtag_id', 'file_id'],
        ]
