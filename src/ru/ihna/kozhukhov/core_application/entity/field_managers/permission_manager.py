from django.conf import settings
from django.db import connection
from django.utils.module_loading import import_string

from .entity_value_manager import EntityValueManager
from ...exceptions.entity_exceptions import EntityOperationNotPermitted
from ..readers.model_emulators import ModelEmulator
from ..readers.query_builders.query_filters import StringQueryFilter


class PermissionManager(EntityValueManager):
    """
    This is the base class for ProjectPermissionManager and AppPermissionManager that
    allows to access the entity permission list.
    """

    _permission_model = None
    """ Defines particular model connects your entity model, the Group model and particular access level """

    _permission_table = None
    """ Defines the SQL table where permission information is stored """

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
    def permission_table(self):
        if self._permission_table is None:
            raise NotImplementedError("Please, define the _permission_table class property")
        return self._permission_table

    @property
    def entity_link_field(self):
        if self._entity_link_field is None:
            raise NotImplementedError("Please, define the _entity_link_field class property")
        return self._entity_link_field

    def __iter__(self):
        """
        Iterates over all permission set
        """
        from ...entity.providers.model_providers.group_provider import GroupProvider
        from ...entity.providers.model_providers.access_level_provider import AccessLevelProvider

        group_provider = GroupProvider()
        level_provider = AccessLevelProvider()

        self._check_system_permissions(None, None)
        query = self.__build_iteration_query()
        for group, access_level in self.__iterate_with_query(query, group_provider, level_provider):
            yield group, access_level

    def set(self, group, access_level):
        """
        Sets the access level to a particular group.

        :param group: a group to which access level must be set. Setting so called 'default access level' to the None
            group is not supported since I don't have much time to implement this
        :param access_level: the access level to set (an instance of AccessLevel entity)
        :return: nothing
        """
        self._check_system_permissions(group, access_level)
        if group is None:
            if access_level.alias == "no_access":
                return
            else:
                raise EntityOperationNotPermitted()
        if group.id == self.entity.root_group.id:
            if access_level.alias == "full":
                return
            else:
                raise EntityOperationNotPermitted()
        try:
            permission = self.permission_model.objects.get(**{
                self.entity_link_field: self._get_entity_id(self.entity),
                "group_id": group.id
            })
            permission.access_level_id = access_level.id
            permission.save()
        except self.permission_model.DoesNotExist:
            permission = self.permission_model(**{
                self.entity_link_field: self._get_entity_id(self.entity),
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
        from ..entity_sets.access_level_set import AccessLevelSet

        self._check_system_permissions(group, None)
        try:
            try:
                permission = self.permission_model.objects.get(**{
                    self.entity_link_field: self._get_entity_id(self.entity),
                    "group_id": group.id
                })
            except (self.permission_model.DoesNotExist, AttributeError):
                permission = self.permission_model.objects.get(**{
                    self.entity_link_field: self._get_entity_id(self.entity),
                    "group_id": None
                })
            access_level_set = AccessLevelSet()
            return access_level_set.get(permission.access_level_id)  # +1 EXTRA SQL QUERY!
        except (self.permission_model.DoesNotExist, AttributeError):
            access_level_set = AccessLevelSet()
            return access_level_set.get("no_access")

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
                self.entity_link_field: self._get_entity_id(self.entity),
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

    def _get_entity_id(self, entity):
        """
        Returns the entity ID.

        :return: the entity id
        """
        return entity.id

    def __build_iteration_query(self):
        builder = settings.QUERY_BUILDER_CLASS()
        builder \
            .add_select_expression("core_application_group.id") \
            .add_select_expression("core_application_group.name") \
            .add_select_expression("core_application_user.id") \
            .add_select_expression("core_application_user.login") \
            .add_select_expression("core_application_user.name") \
            .add_select_expression("core_application_user.surname") \
            .add_select_expression("core_application_accesslevel.id") \
            .add_select_expression("core_application_accesslevel.alias") \
            .add_select_expression("core_application_accesslevel.name") \
            .add_data_source(self.permission_table) \
            .set_main_filter(StringQueryFilter("%s.%s=%%s" % (self.permission_table, self.entity_link_field),
                                               self.entity.id)) \
            .add_order_term("%s.group_id IS NULL" % self.permission_table, builder.ASC) \
            .add_order_term("core_application_group.name", builder.ASC)
        builder.data_source \
            .add_join(builder.JoinType.LEFT, "core_application_group",
                      "ON (core_application_group.id=%s.group_id)" % self.permission_table) \
            .add_join(builder.JoinType.LEFT, "core_application_groupuser",
                      "ON (core_application_groupuser.group_id=core_application_group.id "
                      "AND core_application_groupuser.is_governor)") \
            .add_join(builder.JoinType.LEFT, "core_application_user",
                      "ON (core_application_user.id=core_application_groupuser.user_id)") \
            .add_join(builder.JoinType.INNER, "core_application_accesslevel",
                      "ON (core_application_accesslevel.id=%s.access_level_id)" % self.permission_table)
        query = builder.build()
        return query

    def __iterate_with_query(self, query, group_provider, level_provider):
        with connection.cursor() as cursor:
            cursor.execute(query[0], query[1:])
            for group_id, group_name, governor_id, governor_login, governor_name, governor_surname,\
                    level_id, level_alias, level_name in cursor.fetchall():
                if group_id is not None:
                    group_object = ModelEmulator(
                        id=group_id,
                        name=group_name,
                        governor=ModelEmulator(
                            id=governor_id,
                            login=governor_login,
                            name=governor_name,
                            surname=governor_surname
                        )
                    )
                    group = group_provider.wrap_entity(group_object)
                else:
                    group = None
                level_object = ModelEmulator(
                    id=level_id,
                    alias=level_alias,
                    name=level_name
                )
                access_level = level_provider.wrap_entity(level_object)
                yield group, access_level
