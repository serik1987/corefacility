from django.db import models
from django.utils.translation import gettext_lazy as _


class LevelType(models.TextChoices):
    """
    Defines a type of the access level

    There are two types of the access level:
    project_level defines base access levels to the project
    app_level defines additional restrictions that can be applied to a certain application
    """
    project_level = "prj", _("Project access level")
    app_level = "app", _("Application access level")
