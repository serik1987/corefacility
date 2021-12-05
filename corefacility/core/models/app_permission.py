from django.db import models
from .permission import Permission
from .enums import LevelType


class AppPermission(Permission):
    """
    Defines some additional restrictions that will be applied to the application
    """
    group = models.ForeignKey("Group", null=True, editable=False,
                              on_delete=models.CASCADE,
                              help_text="The user group that also has an access to the project")
    application = models.ForeignKey("Module", on_delete=models.CASCADE, related_name="permissions",
                                    help_text="The application which permissions are described here")

    class Meta:
        unique_together = ["group", "application"]
