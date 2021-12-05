from django.db import models


class LogLevel(models.TextChoices):
    """
    Describes various log levels
    """
    DEBUG = "DBG", "Debugging message"
    INFO = "INF", "Information message"
    WARNING = "WRN", "The system warning"
    ERROR = "ERR", "The system error"
    CRITICAL = "CRI", "The system was down"
