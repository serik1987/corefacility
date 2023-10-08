from django.db import models
from .enums import LogLevel


class LogRecord(models.Model):
    """
    Defines a single log record

    Difference requests may report about their preliminary stages. Such reports will be
    saved here
    """
    log = models.ForeignKey("Log", related_name="records", on_delete=models.CASCADE, editable=False)
    record_time = models.DateTimeField(db_index=True, editable=False)
    level = models.CharField(max_length=3, db_index=True, editable=False, default="DBG",
                             choices=LogLevel.choices)
    message = models.CharField(max_length=1024, editable=False)

    class Meta:
        ordering = ["record_time"]
