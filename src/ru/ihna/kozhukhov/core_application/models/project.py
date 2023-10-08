from django.db import models


class Project(models.Model):
    """
    Defines the project information that will be stored in the database
    """
    alias = models.SlugField(max_length=64, unique=True)
    avatar = models.ImageField(null=True)
    name = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.TextField(null=True)
    root_group = models.ForeignKey("Group", on_delete=models.RESTRICT)
    project_dir = models.CharField(max_length=100, unique=True, null=True, editable=False)
    unix_group = models.CharField(max_length=11, unique=True, null=True, editable=False)

    class Meta:
        ordering = ["name"]
