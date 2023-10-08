from django.db import models


class AccessLevel(models.Model):
    """
    Defines how information about certain access level will be stored in the database

    Access levels is filled during the application installation routines
    """
    alias = models.SlugField(editable=False)
    name = models.CharField(max_length=64, editable=False)
