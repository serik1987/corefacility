from django.db import models
from .permission import Permission
from .enums import LevelType


class ProjectPermission(Permission):
    """
    Stores the access level for a particular user group within the database

    Project permission is user-defined
    """
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="permissions",
                                help_text="The project to which the user group has an additional access")

    class Meta:
        unique_together = ["group", "project"]
