from core.os import CommandMaker, exceptions as os_exceptions

from ..views.base_view_test import BaseViewTest


class TestCommandMaker(BaseViewTest):
    """
    Provides the command maker tests
    """

    @staticmethod
    def is_posix():
        try:
            import posix
            return True
        except ImportError:
            return False

    def test_singleton(self):
        """
        Tests that the command maker class is singleton

        :return: nothing
        """
        maker1 = CommandMaker()
        maker2 = CommandMaker()
        self.assertIs(maker1, maker2, "The CommandMaker must be singleton")

    def test_normal_flow(self):
        """
        Tests the normal flow of the command maker: initialize executor -> initialize command queue -> add command
            -> run_all_commands -> clear_executor

        :return: nothing
        """
        if not self.is_posix():
            self.skipTest("This test is for UNIX operating systems only")
        with self.settings(CORE_UNIX_ADMINISTRATION=True, CORE_SUGGEST_ADMINISTRATION=False):
            maker = CommandMaker()
            maker.initialize_executor(self)
            maker.initialize_command_queue()
            maker.add_command(("ls", "-l"))
            maker.run_all_commands()
            maker.clear_executor(self)

    def test_error_flow(self):
        """
        Tests the error command execution

        :return: nothing
        """
        if not self.is_posix():
            self.skipTest("This is for UNIX operating systems only")
        with self.settings(CORE_UNIX_ADMINISTRATION=True, CORE_SUGGEST_ADMINISTRATION=False):
            maker = CommandMaker()
            maker.initialize_executor(self)
            maker.initialize_command_queue()
            maker.add_command(("ls", "fisghjfhrvj"))
            maker.add_command(("cat", "/etc/passwd"))
            with self.assertRaises(os_exceptions.OsCommandFailedError,
                                   msg="Incorrect command must raise OsCommandFailedError"):
                maker.run_all_commands()
            maker.clear_executor(self)

    def test_configuration_suggestion(self):
        """
        Tests the configuration suggestion for the operating system

        :return: nothing
        """
        with self.settings(CORE_UNIX_ADMINISTRATION=False, CORE_SUGGEST_ADMINISTRATION=True):
            maker = CommandMaker()
            maker.initialize_executor(self)
            maker.initialize_command_queue()
            maker.add_command(("ls", "-l"))
            maker.add_command(("cat", "/etc/passwd"))
            with self.assertRaises(os_exceptions.OsConfigurationSuggestion,
                                   msg=""):
                maker.run_all_commands()
            maker.clear_executor(self)

    def test_configuration_simple(self):
        """
        Tests the command running in the idle mode

        :return: nothing
        """
        with self.settings(CORE_UNIX_ADMINISTRATION=False, CORE_SUGGEST_ADMINISTRATION=False):
            maker = CommandMaker()
            maker.initialize_executor(self)
            maker.initialize_command_queue()
            maker.add_command(("ls", "dfkjkjdf"))
            maker.add_command(("cat", "/etc/shadow"))
            maker.run_all_commands()
            maker.clear_executor(self)

    def test_synchronicity_error(self):
        """
        Tests whether synchronicity error will be risen when normal command flow has been interrupted

        :return:
        """
        with self.settings(CORE_UNIX_ADMINISTRATION=True, CORE_SUGGEST_ADMINISTRATION=False):
            maker = CommandMaker()
            maker.initialize_executor(self)
            maker.initialize_executor(list())
            maker.initialize_command_queue()
            maker.run_all_commands()
            with self.assertRaises(os_exceptions.SynchronicityError, msg="The synchronicity check failed"):
                maker.clear_executor(self)
