from core.entity.entry_points.synchronizations import SynchronizationModule


class IhnaSynchronization(SynchronizationModule):
    """
    Provides synchronization through the IHNA website for demonstration and testing
    """

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
