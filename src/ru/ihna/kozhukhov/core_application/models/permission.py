from django.db import models


class Permission(models.Model):
    """
    Stores the access level for a particular user group within the database

    Project permission is user-defined
    """
    group = models.ForeignKey("Group", null=True, editable=False,
                              on_delete=models.CASCADE, related_name="permissions")
    access_level = models.ForeignKey("AccessLevel", on_delete=models.CASCADE)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="permissions")

    class Meta:
        unique_together = ["group", "project"]
