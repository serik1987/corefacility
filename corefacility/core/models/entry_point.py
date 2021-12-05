from django.db import models
from .enums import EntryPointType


class EntryPoint(models.Model):
    """
    The application module can be attached to the application through a certain
    'entry point'. Each entry point
    """
    alias = models.SlugField(help_text="A short name that can be used to identify the entry point in the app")
    belonging_module = models.ForeignKey("Module", on_delete=models.CASCADE, related_name="entry_points",
                                         editable=False,
                                         help_text="a module having this entry point")
    name = models.CharField(max_length=128, editable=False,
                            help_text="The name through which the entry point is visible on the system")
    type = models.CharField(max_length=3, editable=False, default="lst", choices=EntryPointType.choices,
                            help_text="Whether the entry point looks like list or select?")

    class Meta:
        unique_together = ["alias", "belonging_module"]
