from django.db import models


class Log(models.Model):
    """
    Defines how a single log record will be stored in the database

    API requests only will be logged
    """
    request_date = models.DateTimeField(editable=False, db_index=True)
    log_address = models.CharField(max_length=4096, editable=False)
    request_method = models.CharField(max_length=7, editable=False)
    operation_description = models.CharField(max_length=4096, editable=False, null=True)
    request_body = models.TextField(editable=False, null=True)
    input_data = models.TextField(editable=False, null=True)
    user = models.ForeignKey("User", editable=False, null=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(editable=False, null=True)
    geolocation = models.CharField(max_length=256, null=True, editable=False)
    response_status = models.IntegerField(null=True, editable=False)
    response_body = models.TextField(editable=False, null=True,
                                     help_text="defines the response body")
    output_data = models.TextField(editable=False, null=True)

    class Meta:
        ordering = ["-request_date"]
