from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Working with automatic administration requests.

    When you add users, groups or projects under PartServerConfiguration or FullServerConfiguration, the gunicorn
    worker process can't update Linux users and groups database because it doesn't run under the root. Instead of
    it, such a process adds so called 'posix request' to the core_application_posixrequest table in the database.

    This command must be run under 'root' privileges. It extracts such information and executes given POSIX command.
    The command can act standalone as well as together with the 'corefacility' daemon that has run upon the startup.
    """

    def handle(self, *args, **kwargs):
        """
        Handles the CLI command

        :param args: additional positioned arguments from the command line
        :param kwargs: additional non-positioned arguments from the command line
        """
        print(args)
        print(kwargs)
