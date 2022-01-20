from django.db import models
from .enums import LogLevel


class LogRecord(models.Model):
    """
    Defines a single log record

    Difference requests may report about their preliminary stages. Such reports will be
    saved here
    """
    log = models.ForeignKey("Log", related_name="records", on_delete=models.CASCADE, editable=False,
                            help_text="Log to which this record belongs to")
    record_time = models.DateTimeField(db_index=True, editable=False,
                                       help_text="Date and time when this record has been created")
    level = models.CharField(max_length=3, db_index=True, editable=False, default="DBG",
                             choices=LogLevel.choices,
                             help_text="The importance of this log message")
    message = models.CharField(max_length=1024, editable=False,
                               help_text="The log message itself")

    class Meta:
        ordering = ["record_time"]
