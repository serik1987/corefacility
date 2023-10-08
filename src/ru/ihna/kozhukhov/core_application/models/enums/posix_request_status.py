from django.db import models


class PosixRequestStatus(models.TextChoices):
    """
    Defines different statuses of a request from the remote user connecting to the server via HTTP and POSIX
    administrative functions.
    """

    INITIALIZED = "I"
    ANALYZED = "A"
    CONFIRMED = "C"
