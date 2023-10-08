from time import sleep
from django.core.management.base import BaseCommand

from ...entry_points import SynchronizationsEntryPoint


class Command(BaseCommand):
    """
    Provides an account synchronization process
    """

    help = "Synchronizes users and groups with some external service"
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
            self.stdout.write("\033[32mSynchronization step: {step}.\033[0m Synchronization options: {options}".format(
                step=synchronization_step, options=options
            ))
            synchronization_result = SynchronizationsEntryPoint.synchronize(**options)
            synchronization_started = True
            options = synchronization_result["next_options"]
            for error_details in synchronization_result["details"]:
                self.stdout.write("\033[31m[{message_code}] {message}\033[0m".format(
                    message_code=error_details["message_code"],
                    message=error_details["message"]
                ))
                self.stdout.write("Error source: {name} {surname} ({login})".format(
                    name=error_details["name"],
                    surname=error_details["surname"],
                    login=error_details["login"],
                ))
            synchronization_step += 1
            sleep(self.TECHNICAL_PAUSE)
