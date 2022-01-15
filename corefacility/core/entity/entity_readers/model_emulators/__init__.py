"""
Model emulators are objects that processes by the ModelProvider's wrap_entity method in the same way as
real Django models. Model emulators are the main connectors between RawSqlQueryReader and entity providers.
"""
import pytz
from django.utils import timezone


class ModelEmulator:
    """
    The main model emulator class that translates array keys to real properties.
    """

    __wrapped = None

    def __init__(self, **kwargs):
        """
        Initializes the model emulator

        :param kwargs: raw values for entity field
        """
        self.__wrapped = kwargs

    def __getattr__(self, name):
        """
        The wrap_entity method usually query object's attributes which names are the same as property field names.
        The main goal of this emulator is to give proper value from the dictionary.

        :param name: the field name
        :return: the field value
        """
        try:
            return self.__wrapped[name]
        except KeyError:
            raise AttributeError("The external object doesn't have the following field: " + name)


ModelEmulatorFileField = ModelEmulator


def time_from_db(time):
    """
    When you load the time from the database the time is given relatively to the UTC timezone with no timezone info.
    Use this function to transform it to the local time with timezone given

    :param time: time read from the database
    :return: local time with the local timezone given
    """
    if time is not None:
        time = timezone.make_aware(time, timezone=pytz.UTC)
        time = timezone.localtime(time)
    return time
