import logging

from colorama import Fore, Style
from django.conf import settings


class DebugFilter(logging.Filter):
    """
    Passes all loggings except DEBUG if DEBUG setting is True.

    Passes all loggings including DEBUG if DEBUG setting is False.
    """

    def filter(self, record):
        return settings.DEBUG or record.levelno > logging.DEBUG


class ConsoleFormatter(logging.Formatter):
    """
    Formats the logging information in such a way as different log levels are colored by different colors.
    """

    def format(self, record):
        if record.levelno == logging.WARNING:
            return Fore.YELLOW + super().format(record) + Style.RESET_ALL
        elif record.levelno == logging.ERROR:
            return Fore.RED + super().format(record) + Style.RESET_ALL
        elif record.levelno == logging.CRITICAL:
            return Fore.RED + Style.BRIGHT + super().format(record) + Style.RESET_ALL
        else:
            return super().format(record)


class DatabaseHandler(logging.Handler):
    """
    Saves the log information to the database
    """

    def emit(self, record):
        if hasattr(record, "request") and not hasattr(record.request, "corefacility_log"):
            return
        try:
            if hasattr(record, "request") and hasattr(record.request, "corefacility_log"):
                log = record.request.corefacility_log
            else:
                from core.entity.log import Log
                log = Log.current()
            log.add_record(record.levelname[:3], record.getMessage())
        except Exception:
            aux_logger = logging.getLogger("django.corefacility.log")
            aux_logger.critical("The log above was not written to the database. Please, check whether log emitting is "
                                "suitable")
