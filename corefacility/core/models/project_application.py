from django.db import models


class ProjectApplication(models.Model):
    """
    Organizes Create, Read, Update and Delete operations with the database related to the project application info
    """

    application = models.ForeignKey("core.Module", on_delete=models.CASCADE)
    project = models.ForeignKey("core.Project", on_delete=models.CASCADE)
    is_enabled = models.BooleanField(null=False, blank=False, db_index=True)

    class Meta:
        unique_together = ("application", "project")
