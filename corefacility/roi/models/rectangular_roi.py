from django.db import models


class RectangularRoi(models.Model):
    """
    Stores information about the rectangular ROI in the database
    """
    map = models.ForeignKey("imaging.Map", on_delete=models.CASCADE, related_name="rectangular_roi",
                            help_text="A map to which this ROI is attached")
    left = models.PositiveIntegerField(help_text="ROI left border")
    right = models.PositiveIntegerField(help_text="ROI right border")
    top = models.PositiveIntegerField(help_text="ROI top border")
    bottom = models.PositiveIntegerField(help_text="ROI bottom border")
