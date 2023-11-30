import re
import subprocess

from django.conf import settings

from ....exceptions.entity_exceptions import ConfigurationProfileException, PosixCommandFailedException
from ....models.enums import LogLevel


class AutoAdminObject:
    """
    The class describes an action or set of actions which execution describes administrative privileges.

    The class informs the autoadmin that the required method which name is stored in the database is safe to execute.
    This means that if the required method doesn't belong to an object that is descendant of the
    """

    _static_objects = None

    log = None
    """ Log to be attached to the AutoAdminObject (allows to use the AutoAdminWrapperObject as wrapper on it). """

    command_emulation = True
    """ Prints commands to the command buffer, instead of execution of them """

    _command_buffer = None

    _quote_needed_pattern = re.compile(r"\s")

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
        self._command_buffer = list()

    def flush_command_buffer(self):
        """
        Returns all strings from the command buffer and clears it.
        """
        command_list = []
        for command in self._command_buffer:
            command_string = self._get_command_string(command)
            command_list.append(command_string)
        self._command_buffer = list()
        return "\r\n".join(command_list)

    def copy_command_list(self, destination):
        """
        Copies command list from here to another AutoAdminObject.
        The command buffer will be flushed after this operation. When the command emulation mode is turned off,
        the function does nothing.

        :param destination: another AutoAdminObject to copy to.
        """
        if self.command_emulation:
            for command in self._command_buffer:
                destination.run(command)
            self._command_buffer = list()

    def call(self, posix_request):
        """
        Calls a method stored into the database

        :param posix_request: a model that reflects a given row in the database related to the POSIX request
        :return: the same value as returned by the called method
        """
        from .utils import deserialize_all_args
        request_method = getattr(self, posix_request.method_name)
        args, kwargs = deserialize_all_args(posix_request.method_arguments)
        return request_method(*args, **kwargs)

    def run(self, cmd, *args, **kwargs):
        """
        Calls the UNIX command using the subprocess(...) routine

        :param cmd: the command to execute
        :param args: arguments to the subprocess.call
        :param kwargs: keyword arguments to the subprocess.call
        :return: combined stdout + stderr output
        """
        if self.command_emulation:
            command = " ".join(cmd)
            self._command_buffer.append(cmd)
            return command
        else:
            command_string = self._get_command_string(cmd)
            self.log.add_record(LogLevel.INFO, command_string)
            try:
                kwargs.update({
                    "stdout": subprocess.PIPE,
                    "stderr": subprocess.STDOUT,
                    "check": True,
                })
                result = subprocess.run(cmd, *args, **kwargs)
                output = result.stdout.decode("utf-8")
                if output != "" and output is not None:
                    self.log.add_record(LogLevel.INFO, output)
                return output
            except subprocess.CalledProcessError as error:
                output = error.stdout.decode("utf-8")
                self.log.add_record(LogLevel.ERROR, output)
                raise PosixCommandFailedException(command_string, output)

    def _get_command_string(self, command):
        """
        Transforms the command to the command string

        :param command: a tuple that represents a command to execute
        :return: a string that represents a command
        """
        if isinstance(command, str):
            return command
        quoted_command = [
            '"%s"' % cmd_part
            if self._quote_needed_pattern.search(cmd_part) is not None or cmd_part == "" else cmd_part
            for cmd_part in command
        ]
        command_string = " ".join(quoted_command)
        return command_string
