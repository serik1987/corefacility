from django.db import models


class Project(models.Model):
    """
    Defines the project information that will be stored in the database
    """
    alias = models.SlugField(unique=True,
                             help_text="A short string that is needed to build the project URL")
    avatar = models.ImageField(null=True,
                               help_text="The project image to be shown on the project list")
    name = models.CharField(max_length=512, unique=True, db_index=True,
                            help_text="The project name to display")
    description = models.TextField(null=True,
                                   help_text="Short project description, necessary for sending submissions")
    root_group = models.ForeignKey("Group", on_delete=models.RESTRICT,
                                   help_text="The group that created and initialized the project")
    project_apps = models.ManyToManyField("Module",
                                          help_text="List of application visible in the particular project")
    project_dir = models.CharField(max_length=100, unique=True, null=True, editable=False,
                                   help_text="directory where project files will be located")
    unix_group = models.CharField(max_length=11, unique=True, null=True, editable=False,
                                  help_text="unix group related to the project")
