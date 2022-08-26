from enum import Enum
import subprocess
import logging

from django.conf import settings
from django.http.request import HttpRequest

from .exceptions import SynchronicityError, OsConfigurationSuggestion, OsCommandFailedError


class CommandMaker:
    """
    Accepts commands to the UNIX operating system and stores the commands to the temporary buffer.
    When the request is going to be finished, this object executes all commands.

    If all commands complete with return code 0 the request is treated to be completed with the response code 200 OK
    If at least one command complete with return code other than 0 the request is treated to be completed with
        the response code 400 BAD REQUEST. The response body will contain the 'code' field equal to 'posix_error'
    If you use the part-server configuration, the commands will not be executed, the request will be completed with
        response code 400 BAD REQUEST and list of all commands will be printed in the 'detail' field of the
        response body. The 'code' field of the response body will be equal to 'action_required'

    The commands will be executed by means of subprocess.run routine.

    All POSIX commands are executed in the context of so called 'executor'. The executor is either request object or
    Django management command object. Any executor shall be initialized at the beginning of the execution and shall
    be terminated at the end of the execution.
    """

    class Mode(Enum):
        """
        The executor mode.

        SYNC mode means that you can serve just one executor at a time. The SYNC mode requires that the Gunicorn
        works in synchronous mode. In SYNC mode you can't initialize the following executor without clearing the
        previous one.
        ASYNC mode means that you can serve infinite number of executors at a time. The ASYNC mode allows
        the Gunicorn to work in any mode: synchronous, asynchronous etc.

        When the instance is created, the command mode is ASYNC. However, if you use any command maker's method
        with default value of the executor argument (executor=None), the mode will be automatically switched to SYNC.

        """
        SYNC = "Synchronous mode"
        ASYNC = "Asynchronous mode"

    test_flag = False
    """ The test cases provided with the core module are the same for all server configurations. In order to
        run them successfully at the part server configuration please, set up this flag to True at the test's setUp.
        In this case the server account will not be synchronized with the POSIX accounts for any system configuration.
        """

    _instance = None
    """ A single instance of the class """

    _mode = None
    """ Current execution mode """

    _executor = None
    """ Current executor """

    _execution_queue = None
    """ The current execution queue """

    _message_queue = None
    """ The message queue. All commands will be stored in the message queue """

    _logger = logging.getLogger("django.corefacility.posix")

    @property
    def executor(self):
        """
        A current HTTP request or the server management command to which this maker has been attached
        """
        return self._executor

    def __new__(cls):
        """
        Returns an existent instance of the CommandMaker.

        If the instance has not been created, it will be created automatically
        """
        if cls._instance is None:
            cls._instance = super(CommandMaker, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the internal fields of the command maker.
        """
        if self._execution_queue is None:
            self._execution_queue = dict()
        if self._mode is None:
            self._mode = self.Mode.ASYNC

    def initialize_executor(self, executor):
        """
        Initializes the executor.

        This function must be run at the very beginning of the request or command

        :param executor: the executor to be initialized
        :return: nothing
        """
        executor_id = id(executor)
        self._executor = executor
        self._execution_queue[executor_id] = list()

    def initialize_command_queue(self, executor=None):
        """
        Initializes the command queue. All existent commands win the command queue will be deleted.

        :param executor: the executor itself or None if you want to use the executor put during the last call
            of the initialize_executor function
        :return:
        """
        executor = self._get_executor(executor)
        self._execution_queue[id(executor)] = list()

    def add_command(self, *args, executor=None, **kwargs):
        """
        Adds command to the command queue.

        :param args: Arguments to the subprocess.run routine
        :param executor: the executor or None if you want to use the executor added at the last call of the
            initialize_executor function
        :param kwargs: Keyword arguments to the subprocess.run routine
        :return: nothing
        """
        if executor is not None or self._executor is not None:
            executor = self._get_executor(executor)
            self._execution_queue[id(executor)].append({"args": args, "kwargs": kwargs})

    def run_all_commands(self, executor=None, flush_message_queue=True):
        """
        Run commands that are added previously to the executor

        :param executor: the executor or None if you want to use the executor added at the last call of the
            initialize_executor function
        :return: nothing
        """
        executor = self._get_executor(executor)
        execution_queue = self._execution_queue[id(executor)]
        self._message_queue = list()
        if not self.test_flag:
            if settings.CORE_UNIX_ADMINISTRATION:
                for command in execution_queue:
                    self._execute(executor, *command["args"], **command["kwargs"])
            if settings.CORE_SUGGEST_ADMINISTRATION and len(execution_queue) > 0:
                raise OsConfigurationSuggestion(execution_queue)
        self._execution_queue[id(executor)] = list()
        if flush_message_queue:
            self.flush_message_queue(executor)

    def flush_message_queue(self, executor):
        if hasattr(self.executor, "corefacility_log"):
            for message in self._message_queue:
                if message['message'] == '' or message['message'] is None:
                    message['message'] = "The command has been printed no new messages!"
                executor.corefacility_log.add_record(message['level'], message['message'])
        self._message_queue = list()

    def clear_executor(self, executor):
        if self._mode == self.Mode.SYNC and executor is not self._executor:
            raise SynchronicityError("Attempt to attach two executors concurrently at synchronous mode")
        self._executor = None
        del self._execution_queue[id(executor)]

    def _get_executor(self, executor):
        """
        Gets the executor

        :param executor: is None, turns the maker into SYNC mode the returns the last executor passed to the
            initialize_executor. If not None, returns the executor
        :return: nothing
        """
        if self._mode == self.Mode.SYNC and executor is not None and executor is not self._executor:
            raise SynchronicityError("The executor {0} be used after executor {1} has been initialized".format(
                executor, self._executor
            ))
        if executor is None:
            self._mode = self.Mode.SYNC
            executor = self._executor
        if id(executor) not in self._execution_queue:
            raise SynchronicityError("The executor {0} has not been initialized".format(executor))
        return executor

    def _execute(self, executor, *args, **kwargs):
        """
        Directly executes the POSIX command using the subprocess.run function

        :param executor: the executor to use
        :param args: arguments for the subprocess.run function
        :param kwargs: keyword arguments for the subprocess.run function
        :return: nothing
        """
        kwargs.update(capture_output=True, check=True)
        try:
            result = subprocess.run(*args, **kwargs)
            self._message_queue.append({"level": "INF", "message": result.stdout.decode("utf-8")})
        except subprocess.CalledProcessError as err:
            cmd = err.cmd
            if isinstance(cmd, list) or isinstance(cmd, tuple):
                cmd = " ".join(cmd)
            msg = "The command '%s' has been returned with status code %d. Reason: %s" % \
                  (cmd, err.returncode, err.stderr.decode("utf-8"))
            self._message_queue.append({"level": "ERR", "message": msg})
            raise OsCommandFailedError(msg)
