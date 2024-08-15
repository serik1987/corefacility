from django.db import models
from django.utils.translation import gettext_lazy as _


class LabjournalFieldType(models.TextChoices):
    """
    Represents different types of the labjournal custom field
    """

    boolean = "B", _("Boolean field")
    string = "S", _("String")
    number = "N", _("Integer or float number")
    discrete = "D", _("Discrete")
