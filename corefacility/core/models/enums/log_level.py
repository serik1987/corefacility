from django.db import models
from django.utils.translation import gettext_lazy as _


class LogLevel(models.TextChoices):
    """
    Describes various log levels
    """
    DEBUG = "DBG", _("Debugging message")
    INFO = "INF", _("Information message")
    WARNING = "WRN", _("The system warning")
    ERROR = "ERR", _("The system error")
    CRITICAL = "CRI", _("The system was down")
