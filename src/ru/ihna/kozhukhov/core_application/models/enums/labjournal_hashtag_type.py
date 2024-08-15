from django.db import models
from django.utils.translation import gettext_lazy as _


class LabjournalHashtagType(models.TextChoices):
    """
    Represents different types of the labjournal hashtags
    """

    record = "R", _("Record hashtag")
    file = "F", _("File hashtag")
