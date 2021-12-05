from django.db import models


class Permission(models.Model):
    """
    A base class for project and application permission
    """
    group = models.ForeignKey("Group", null=True, editable=False,
                              on_delete=models.CASCADE, related_name="permissions",
                              help_text="The user group that also has an access to the project")
    access_level = models.ForeignKey("AccessLevel", on_delete=models.CASCADE,
                                     help_text="A certain access level")

    class Meta:
        abstract = True
