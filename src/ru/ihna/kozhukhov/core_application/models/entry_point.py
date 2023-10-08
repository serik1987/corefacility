from django.db import models
from .enums import EntryPointType


class EntryPoint(models.Model):
    """
    The application module can be attached to the application through a certain
    'entry point'. Each entry point
    """
    alias = models.SlugField()
    belonging_module = models.ForeignKey("Module", on_delete=models.CASCADE, related_name="entry_points",
                                         editable=False)
    name = models.CharField(max_length=128, editable=False)
    type = models.CharField(max_length=3, editable=False, default="lst", choices=EntryPointType.choices)
    entry_point_class = models.CharField(max_length=1024, editable=False)

    class Meta:
        unique_together = ["alias", "belonging_module"]
