from ..entity_provider import EntityProvider


class PosixProvider(EntityProvider):
    """
    The class implements a basic interaction between entities and POSIX commands
    """

    force_disable = False
    """ Switch this option to True for the testing purpose """

    def is_provider_on(self):
        """
        Defines whether the provider is enabled. When the provider is disabled it applies as if it doesn't present
        in the system

        :return: True if the provider is enabled, False otherwise.
        """
        raise NotImplementedError("is_provider_on")

    def attach_file(self, entity, name, value):
        """
        Does nothing because binary data attachment to the POSIX user and group is not supported
        :param entity: the entity to which the file can be attached
        :param name: the field name to which the file should be attached
        :param value: an instance of django.core.files.File object
        :return: nothing
        """
        pass

    def detach_file(self, entity, name):
        """
        Does nothing because binary data detachment from the POSIX user and group is not supported
        :param entity: the entity from which the file shall be detached
        :param name: the field name from which the file should be detached
        :return: nothing
        """
        pass
