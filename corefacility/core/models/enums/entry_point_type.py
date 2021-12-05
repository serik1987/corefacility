from django.db import models


class EntryPointType(models.TextChoices):
    """
    Defines the list of entry point types
    """
    list = "lst", "As list (the user can enable arbitrary amount of modules in this entry point)"
    select = "sel", "as choice (the user myst choice which module in this entry point to enable)"
