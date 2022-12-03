from time import sleep

from django.core.management import BaseCommand

from core.entity.entry_points import SynchronizationsEntryPoint
from core.os.os_command import OsCommand


class Command(OsCommand):
    """
    Provides an account synchronization process
    """

    requires_migrations_checks = True

    TECHNICAL_PAUSE = 1.0

    def handle(self, *args, **kwargs):
        """
        Starts the synchronization process

        :param args: arguments
        :param kwargs: keyword arguments
        :return: nothing
        """
        synchronization_started = False
        options = None
        synchronization_step = 0
        while not synchronization_started or options is not None:
            if options is None:
                options = {}
            print("\033[32mSynchronization step: {step}.\033[0m Synchronization options: {options}".format(
                step=synchronization_step, options=options
            ))
            synchronization_result = SynchronizationsEntryPoint.synchronize(**options)
            synchronization_started = True
            options = synchronization_result["next_options"]
            for error_details in synchronization_result["details"]:
                print("\033[31m[{message_code}] {message}\033[0m".format(
                    message_code=error_details["message_code"],
                    message=error_details["message"]
                ))
                print("Error source: {name} {surname} ({login})".format(
                    name=error_details["name"],
                    surname=error_details["surname"],
                    login=error_details["login"],
                ))
            synchronization_step += 1
            sleep(self.TECHNICAL_PAUSE)
