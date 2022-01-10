from django.utils.module_loading import import_string

from .entity_value_manager import EntityValueManager
from ...entity_exceptions import EntityOperationNotPermitted


class PermissionManager(EntityValueManager):
    """
    This is the base class for ProjectPermissionManager and AppPermissionManager that
    allows to access the entity permission list.
    """

    _permission_model = None
    """ Defines particular model connects your entity model, the Group model and particular access level """

    _entity_link_field = None
    """ Defines a link that connects particular entity to the permission model mentioned above """

    _access_level_type = None
    """ Accepted access level type """

    @property
    def permission_model(self):
        if self._permission_model is None:
            raise NotImplementedError("Please, define the _permission_model class property")
        if isinstance(self._permission_model, str):
            self._permission_model = import_string(self._permission_model)
        return self._permission_model

    @property
    def entity_link_field(self):
        if self._entity_link_field is None:
            raise NotImplementedError("Please, define the _entity_link_field class property")
        return self._entity_link_field

    @property
    def access_level_type(self):
        if self._access_level_type is None:
            raise NotImplementedError("Please, define the _access_level_type class property")
        return self._access_level_type

    def __iter__(self):
        """
        Iterates over all permission set
        """
        raise NotImplementedError("TO-DO: PermissionManager.__iter__")

    def set(self, group, access_level):
        """
        Sets the access level to a particular group.

        :param group: a group to which access level must be set or None if access level shall be set for the rest
            of users
        :param access_level: the access level to set (an instance of AccessLevel entity)
        :return: nothing
        """
        self._check_system_permissions(group, access_level)
        try:
            permission = self.permission_model.objects.get(**{
                self.entity_link_field: self.entity.id,
                "group_id": group.id
            })
            permission.access_level_id = access_level.id
            permission.save()
        except self.permission_model.DoesNotExist:
            permission = self.permission_model(**{
                self.entity_link_field: self.entity.id,
                "group_id": group.id,
                "access_level_id": access_level.id
            })
            permission.save()

    def get(self, group):
        """
        Reads access level for a certain group.

        WARNING. The method is not optimized according to the number of SQL queries. Use the 'user' filter in the
        ProjectSet for full and comprehensive information.

        :param group: a group to which access level must be set or None if access level shall be set for the rest
            of users
        :return: the AccessLevel entity reflecting a certain access level for the group.
        """
        from core.entity.entity_sets.access_level_set import AccessLevelSet

        self._check_system_permissions(group, None)
        try:
            permission = self.permission_model.objects.get(**{
                self.entity_link_field: self.entity.id,
                "group_id": group.id
            })
        except self.permission_model.DoesNotExist:
            permission = self.permission_model.objects.get(**{
                self.entity_link_field: self.entity.id,
                "group_id": None
            })
        access_level_set = AccessLevelSet()
        access_level_set.type = self.access_level_type
        return access_level_set.get(permission.access_level_id)  # +1 EXTRA SQL QUERY!

    def delete(self, group):
        """
        Removes the access level for a certain group

        :param group: the group for which the access level shall be removed.
        :return: nothing
        """
        self._check_system_permissions(group, None)
        if group is None:
            raise EntityOperationNotPermitted()
        try:
            permission = self.permission_model.objects.get(**{
                self.entity_link_field: self.entity.id,
                "group_id": group.id
            })
            permission.delete()
        except self.permission_model.DoesNotExist:
            pass

    def _check_system_permissions(self, group, access_level):
        """
        Checks whether permission list can be changed

        :param group: the group level or None if no group specified
        :param access_level: the access level or None if no access specified
        :return: nothing
        """
        entity_list = [self.entity]
        if group is not None:
            entity_list.append(group)
        if access_level is not None:
            entity_list.append(access_level)
        for entity in entity_list:
            if entity.state in {"creating", "deleted"}:
                raise EntityOperationNotPermitted()
        if access_level is not None and access_level.type != self.access_level_type:
            raise EntityOperationNotPermitted()
