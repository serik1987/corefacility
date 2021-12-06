from django.db import models


class Pinwheel(models.Model):
    """
    Stores information about single pinwheel in the database
    """
    map = models.ForeignKey("imaging.Map", on_delete=models.CASCADE, related_name="pinwheels",
                            help_text="A map to which this ROI is attached")
    x = models.PositiveBigIntegerField(help_text="pinwheel abscissa, px")
    y = models.PositiveBigIntegerField(help_text="pinwheel ordinate, px")
