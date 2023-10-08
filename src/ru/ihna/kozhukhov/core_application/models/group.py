from django.db import models


class Group(models.Model):
    """
    Defines the group information that will be stored to the database
    """
    name = models.CharField(max_length=256, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]
