from django.db import models


class AppPermission(models.Model):
    """
    Defines some additional restrictions that will be applied to the application
    """
    group = models.ForeignKey("Group", null=True,
                              on_delete=models.CASCADE,
                              help_text="the user group to which such permissions applied")
    application = models.ForeignKey("Module", on_delete=models.CASCADE, related_name="permissions",
                                    help_text="The application which permissions are described here")
    access_level = models.ForeignKey("AccessLevel", on_delete=models.CASCADE,
                                     help_text="A certain access level to the application. Different applications may "
                                               "add their own access levels to an appropriate table")

    class Meta:
        unique_together = ["group", "application"]
