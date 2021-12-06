from django.db import models
from .enums import LevelType


class AccessLevel(models.Model):
    """
    Defines how information about certain access level will be stored in the database

    Access levels is filled during the application installation routines
    """
    type = models.CharField(max_length=3, choices=LevelType.choices, default='app', editable=False,
                            help_text="Defines whether this is an application access level or text access level")
    alias = models.SlugField(editable=False,
                             help_text="short name of the access level to use in the API")
    name = models.CharField(max_length=64, editable=False,
                            help_text="Long name of the access level to use in the UI")

    class Meta:
        unique_together = (
            ("type", "alias"),
            ("type", "name")
        )
