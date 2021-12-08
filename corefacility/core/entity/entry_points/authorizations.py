from .entry_point import EntryPoint
from core.entity import CorefacilityModule


class AuthorizationsEntryPoint(EntryPoint):
    """
    The entry point allows you to connect to 'corefacility' additional modules each of this
    can provide various kinds of authorizations: authorization by login and password,
    authorization though Google, authorization through Research Gate and so on.
    """

    def get_alias(self):
        """
        The entry point alias is also the same

        :return: 'authorizations'
        """
        return "authorizations"

    def get_name(self):
        """
        Provides the entry point name visible in the UI

        :return: the entry point name visible in the UI
        """
        return "Authorization methods"

    def get_type(self):
        return "lst"


class AuthorizationModule(CorefacilityModule):
    """
    Defines common methods of all modules attached to the 'authorizations' module.

    This includes not only override of all abstract properties but also contract of
    interaction with the 'core' module
    """

    def get_parent_entry_point(self):
        """
        All authorization applications must be attached to the 'authorizations' entry point

        :return: the parent entry point
        """
        return AuthorizationsEntryPoint()

    def is_application(self):
        """
        Since authorization modules shall authorize non-authorized user, they are modules, not applications

        :return: always False
        """
        return False
