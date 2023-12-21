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

    def __str__(self):
        return ("HealthCheck(date={date}, cpu_load={cpu_load}, ram_free={ram_free}, swap_free={swap_free}," +
                "hdd_free={hdd_free}, bytes_sent={bytes_sent}, bytes_received={bytes_received}, " +
                "temperature={temperature})") \
            .format(date=self.date, cpu_load=self.cpu_load, ram_free=self.ram_free, swap_free=self.swap_free,
                    hdd_free=self.hdd_free, bytes_sent=self.bytes_sent, bytes_received=self.bytes_received,
                    temperature=self.temperature)
