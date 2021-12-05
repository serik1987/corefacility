from django.db import models


class ProjectPermission(models.Model):
    """
    Stores the access level for a particular user group within the database

    Project permission is user-defined
    """
    group = models.ForeignKey("Group", null=True, editable=False,
                              on_delete=models.CASCADE, related_name="permissions",
                              help_text="The user group that also has an access to the project")
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="permissions",
                                help_text="The project to which the user group has an additional access")
    access_level = models.ForeignKey("AccessLevel", on_delete=models.CASCADE,
                                     help_text="A certain access level")

    class Meta:
        unique_together = ["group", "project"]
