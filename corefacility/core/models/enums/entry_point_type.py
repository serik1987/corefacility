from django.db import models
from django.utils.translation import gettext_lazy as _


class EntryPointType(models.TextChoices):
    """
    Defines the list of entry point types
    """
    list = "lst", _("As list (the user can enable arbitrary amount of modules in this entry point)")
    select = "sel", _("As select (the user must choice which module in this entry point to enable)")
