from django.db import models


class LevelType(models.TextChoices):
    """
    Defines a type of the access level

    There are two types of the access level:
    project_level defines base access levels to the project
    app_level defines additional restrictions that can be applied to a certain application
    """
    project_level = "prj", "Project access level"
    app_level = "app", "Application access level"
