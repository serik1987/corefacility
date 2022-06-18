from core.entity.entry_points.synchronizations import SynchronizationModule


class IhnaSynchronization(SynchronizationModule):
    """
    Provides synchronization through the IHNA website for demonstration and testing
    """

    @property
    def app_class(self):
        """
        Returns the application class
        """
        return "core.synchronizations.IhnaSynchronization"

    def get_alias(self):
        """
        The application alias

        :return: alias
        """
        return "ihna_employees"

    def get_name(self):
        """
        The synchronization name

        :return: the synchronization name
        """
        return "IHNA RAS account synchronization"

    def synchronize(self, **options):
        """
        Provides an account synchronization.

        :param options: the synchronization options. The synchronization must be successfuly started and successfully
            completed when no options are given.
        :return: a dictionary that contains the following fields:
            next_options - None if synchronization shall be completed. If synchronization has not been completed
                this function shall be run repeatedly with the option mentioned in this field.
                Please, note
            details - some information about all completed actions. The information is useful to be printed out.
        """
        try:
            stage = int(options['stage'])
            if not 0 <= stage < 10:
                stage = 0
        except (KeyError, ValueError):
            stage = 0
        print("Synchronization is in process. Stage # " + str(stage))
        stage += 1
        if stage < 10:
            next_options = {"stage": stage}
        else:
            next_options = None
        return {"next_options": next_options, "details": None}
