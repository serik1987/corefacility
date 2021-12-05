from django.db import models


class Log(models.Model):
    """
    Defines how a single log record will be stored in the database

    API requests only will be logged
    """
    log_address = models.CharField(max_length=4096, editable=False,
                                   help_text="Defines a full route to the request")
    request_method = models.CharField(max_length=5, editable=False,
                                      help_text="The request method")
    operation_description = models.CharField(max_length=4096, editable=False, null=True,
                                             help_text="The operation description")
    request_body = models.TextField(editable=False, null=True,
                                    help_text="The request body when it represented in text format")
    input_data = models.TextField(editable=False, null=True,
                                  help_text="Description of the request input data")
    user = models.ForeignKey("User", editable=False, null=True, on_delete=models.SET_NULL,
                             help_text="User that is authorized or null if no user is authorized")
    ip_address = models.GenericIPAddressField(editable=False, null=True,
                                              help_text="The IP address defined")
    geolocation = models.CharField(max_length=256, null=True, editable=False,
                                   help_text="Geolocation of that IP address")
    response_status = models.IntegerField(null=True, editable=False,
                                          help_text="HTTP response status")
    response_body = models.TextField(editable=False, null=True,
                                     help_text="defines the response body")
    output_data = models.TextField(editable=False, null=True,
                                   help_text="Short description of the output data")
