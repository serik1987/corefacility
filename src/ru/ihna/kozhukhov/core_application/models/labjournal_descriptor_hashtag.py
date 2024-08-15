from django.db import models


class LabjournalDescriptorHashtag(models.Model):
    """
    Links hashtags to descriptors

    Such a link is required to mention list of hashtags where a given custom parameter is applicable
    """

    hashtag = models.ForeignKey(
        "LabjournalHashtag",
        on_delete=models.CASCADE,
        help_text="Hashtag that must be connected to the descriptor",
        null=False,
    )

    descriptor = models.ForeignKey(
        "LabjournalParameterDescriptor",
        on_delete=models.CASCADE,
        help_text="Descriptor that the hashtag is connected to",
        null=False
    )

    class Meta:
        unique_together = [
            ['hashtag_id', 'descriptor_id']
        ]
