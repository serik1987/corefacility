from django.db import models
from django.utils.translation import gettext_lazy as _


class MapType(models.TextChoices):
    """
    Defines the list of all available map types
    """
    orientation = "ori", _("Orientation map")
    direction = "dir", _("Direction map")
