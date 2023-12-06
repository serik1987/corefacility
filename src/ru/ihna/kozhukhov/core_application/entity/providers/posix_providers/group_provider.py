from django.conf import settings

from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.auto_admin_wrapper_object import \
    AutoAdminWrapperObject
from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.posix_connector import PosixConnector
from .posix_provider import PosixProvider


class GroupProvider(PosixProvider):
    """
    Modifies connection between POSIX users and POSIX groups in relation to corefacility group create, modify,
    delete
    """

    def is_provider_on(self):
        """
        True if the provider routines shall be applied, False otherwise
        :return:
        """
        return not self.force_disable and settings.CORE_MANAGE_UNIX_USERS and \
            settings.CORE_MANAGE_UNIX_GROUPS

    def load_entity(self, group):
        """
        Does nothing because not user-group association is required
        """
        pass

    def create_entity(self, group):
        """
        Does nothing because not user-group association is required
        """
        pass

    def resolve_conflict(self, given_user, posix_user):
        """
        Does nothing because not user-group association is required
        """
        pass

    def update_entity(self, group):
        """
        Does nothing because not user-group association is required
        """
        pass

    def delete_entity(self, group):
        """
        Deletes the entity from the external entity source
        :param group: the entity to be deleted
        :return: nothing
        """
        if self.is_provider_on():
            ids = [user.id for user in group.users]
            posix_connector = AutoAdminWrapperObject(PosixConnector, group.log.id)
            posix_connector.log = group.log
            posix_connector.update_connections(ids)
