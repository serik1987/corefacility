from django.db import models
from .enums import MapType


class Map(models.Model):
    """
    Defines the way to store map files in the NUMPY format
    """
    alias = models.SlugField(unique=True, help_text="Defines the model slug to be used in HTTP requests")
    data = models.FileField(help_text="The associated map file")
    type = models.CharField(max_length=3, choices=MapType.choices, null=False, blank=False,
                            help_text="Whether the map is orientational or directional")
    resolution_x = models.PositiveIntegerField(help_text="Map width, px", null=True, blank=True)
    resolution_y = models.PositiveIntegerField(help_text="Map height, px", null=True, blank=True)
    width = models.FloatField(help_text="Map width, um", null=True, blank=True)
    height = models.FloatField(help_text="Map height, um", null=True, blank=True)
