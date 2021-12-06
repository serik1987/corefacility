from django.db import models
from .enums import MapType


class Map(models.Model):
    """
    Defines the way to store map files in the NUMPY format
    """
    map_alias = models.SlugField(help_text="Defines the model slug to be used in HTTP requests")
    map_file = models.FileField(unique=True,
                                help_text="The associated map file")
    map_type = models.CharField(max_length=3, choices=MapType.choices,
                                help_text="Whether the map is orientational or diractional")
