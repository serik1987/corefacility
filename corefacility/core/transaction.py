from django.db import transaction
from django.conf import settings

from core.os import CommandMaker


class CorefacilityTransaction:
    """
    Defines the corefacility transaction.

    The corefacility transaction combines the database transaction and the command transaction.

    The database transaction means that no information can be written to the database when
    exception has been risen

    The OS transaction means that the exception will be risen in such a way as log records will
    be successfully written to the database but any other information remain to be intact.
    """

    _instance = None

    _database_transaction = None

    def __new__(cls):
        """
        During the first call this method creates an instance of the CorefacilityTransaction.

        Each following call will recap the previously created instance
        """
        if cls._instance is None:
            cls._instance = super(CorefacilityTransaction, cls).__new__(cls)
        return cls._instance

    @property
    def database_transaction(self):
        if self._database_transaction is None:
            self._database_transaction = transaction.atomic()
        return self._database_transaction

    def __enter__(self):
        """
        This method will be called immediately before the beginning of each transaction block

        :return: nothing
        """
        self.database_transaction.__enter__()
        maker = CommandMaker()
        if settings.CORE_SUGGEST_ADMINISTRATION or settings.CORE_UNIX_ADMINISTRATION:
            maker.initialize_command_queue()
        return TransactionObject()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        This method will be called immediately after the finish of each transaction block

        :param exc_type: the exception type
        :param exc_val: the exception value
        :param exc_tb: the exception traceback
        :return: nothing
        """
        if exc_type is None:
            try:
                maker = CommandMaker()
                if maker.executor is not None:
                    maker.run_all_commands()
                self.database_transaction.__exit__(None, None, None)
            except Exception as exc:
                self.database_transaction.__exit__(exc.__class__.__name__, exc, exc.__traceback__)
        else:
            self.database_transaction.__exit__(exc_type, exc_val, exc_tb)


class TransactionObject:
    """
    This is a container where all transaction objects were collected
    """

    @property
    def command_maker(self):
        """
        The command maker contains the 'add_command' function that allows you the delayed command execution
        """
        return CommandMaker()
