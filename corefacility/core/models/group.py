from django.db import models


class Group(models.Model):
    """
    Defines the group information that will be stored to the database
    """
    name = models.CharField(max_length=256, unique=True, db_index=True,
                            help_text="The name of the user group to print")
    users = models.ManyToManyField("User", through="GroupUser",
                                   help_text="Users that has been included to that group")

    class Meta:
        ordering = ["name"]
