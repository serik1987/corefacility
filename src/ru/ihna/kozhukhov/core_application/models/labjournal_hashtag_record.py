from django.db import models


class LabjournalHashtagRecord(models.Model):
    """
    Stores links between labjournal records and the record hashtags
    """

    hashtag = models.ForeignKey(
        "LabjournalHashtag",
        on_delete=models.CASCADE,
        null=False,
    )

    record = models.ForeignKey(
        "LabjournalRecord",
        on_delete=models.CASCADE,
        null=False,
    )

    class Meta:
        unique_together = [
            ['hashtag_id', 'record_id'],
        ]
