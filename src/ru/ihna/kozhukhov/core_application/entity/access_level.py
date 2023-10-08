from django.utils.translation import gettext

from .entity import Entity
from ..exceptions.entity_exceptions import EntityOperationNotPermitted
from ru.ihna.kozhukhov.core_application.entity.entity_sets.access_level_set import AccessLevelSet
from .providers.model_providers.access_level_provider import AccessLevelProvider
from .fields import EntityField, ReadOnlyField, EntityAliasField


class AccessLevel(Entity):
    """
    Defines the access level
    """

    _entity_set_class = AccessLevelSet

    _entity_provider_list = [AccessLevelProvider()]

    _required_fields = ["type", "alias", "name"]

    _public_field_description = {
        "type": ReadOnlyField(description="Access level type"),
        "alias": EntityAliasField(max_length=50),
        "name": EntityField(str, min_length=1, max_length=64, description="Access level name")
    }

    def __getattr__(self, name):
        """
        Returns the access level names

        :param name: property name
        :return: value
        """
        value = super().__getattr__(name)
        if name == "name":
            value = gettext(value)
        return value

    def __setattr__(self, name, value):
        """
        Sets the application properties

        :param name: the property name
        :param value: the property value
        :return: nothing
        """
        if name == "alias" and self._alias in ["add", "permission_required", "usage", "no_access"]:
            self._check_system_permissions()
        super().__setattr__(name, value)

    def update(self):
        """
        Saves all changes in the access level to the database

        :return: nothing
        """
        self._check_system_permissions()
        super().update()

    def delete(self):
        """
        Removes the access level from the database

        :return: nothing
        """
        self._check_system_permissions()
        super().delete()

    def _check_system_permissions(self):
        raise EntityOperationNotPermitted()
