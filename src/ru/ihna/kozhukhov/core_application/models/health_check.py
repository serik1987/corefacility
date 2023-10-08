from django.db import models


class HealthCheck(models.Model):
    """
    Stores results of the health check.
    The health check is organized every minute and measures such values of CPU and memory load, temperature,
    network and HDD usage etc.
    This model allows to store such measures in the database.
    """

    date = models.DateTimeField(db_index=True)
    cpu_load = models.JSONField()
    ram_free = models.PositiveBigIntegerField()
    swap_free = models.PositiveBigIntegerField()
    hdd_free = models.JSONField()
    bytes_sent = models.PositiveBigIntegerField()
    bytes_received = models.PositiveBigIntegerField()
    temperature = models.JSONField()
