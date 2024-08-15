from django.db import models
from django.utils.translation import gettext_lazy as _


class LabjournalRecordType(models.TextChoices):
    """
    Represents different type of the laboratory record
    """

    data = "D", _("Data record")
    service = "S", _("Service record")
    category = "C", _("Category record")
