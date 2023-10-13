import subprocess

from django.conf import settings

from ....exceptions.entity_exceptions import ConfigurationProfileException


class AutoAdminObject:
    """
    The class describes an action or set of actions which execution describes administrative privileges.

    The class informs the autoadmin that the required method which name is stored in the database is safe to execute.
    This means that if the required method doesn't belong to an object that is descendant of the
    """

    _static_objects = None

    log = None
    """ Log to be attached to the AutoAdminObject (allows to use the AutoAdminWrapperObject as wrapper on it). """

    @classmethod
    def update_static_objects(cls):
        """
        An auto admin object has some kind of static objects (e.g., POSIX users or group already registered in the
        operating system).

        Use this method to update the object list. Primarily, the method should be run at the beginning of the
        auto admin cycle
        """
        pass

    @classmethod
    def get_static_objects(cls):
        """
        An auto admin object has some kind of static objects (e.g., POSIX users or group already registered in the
        operating system).

        Use this method to update the object list. Primarily, the method should be run at the beginning of the
        auto admin cycle.
        """
        if cls._static_objects is None:
            cls.update_static_objects()
        return cls._static_objects

    def __init__(self):
        """
        Initializes the auto admin object
        """
        if not settings.CORE_UNIX_ADMINISTRATION and not settings.CORE_SUGGEST_ADMINISTRATION:
            raise ConfigurationProfileException(settings.CONFIGURATION)

    def run(self, cmd, *args, **kwargs):
        """
        Calls the UNIX command using the subprocess(...) routine

        :param cmd: the command to execute
        :param args: arguments to the subprocess.call
        :param kwargs: keyword arguments to the subprocess.call
        :return: combined stdout + stderr output
        """
        kwargs.update({
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "check": True,
        })
        result = subprocess.run(cmd, *args, **kwargs)
        return result.stdout.decode("utf-8")
