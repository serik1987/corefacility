from ....models import Project, Permission
from .model_provider import ModelProvider
from .group_provider import GroupProvider
from ...entity_sets.access_level_set import AccessLevelSet


class ProjectProvider(ModelProvider):
    """
    Defines the project model provider. The project model provider allows storing projects on the database
    """

    DEFAULT_ACCESS_LEVEL = "no_access"
    """ The default access level for the rest of users """

    _entity_model = Project
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = "alias"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = ["alias", "avatar", "name", "description", "root_group", "project_dir", "unix_group",
                     "is_user_governor", "user_access_level"]
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.project.Project"
    """
    Defines the entity class (the string notation)
    """

    def create_entity(self, entity):
        """
        Creates the entity in a certain entity source and changes the entity's _id and _wrapped properties
        according to how the entity changes its status.

        :param entity: The entity to be created on this entity source
        :return: nothing but entity provider must fill necessary entity fields
        """
        super().create_entity(entity)
        level_set = AccessLevelSet()
        default_access_level = level_set.get(self.DEFAULT_ACCESS_LEVEL)
        permission = Permission(project_id=entity.id, group_id=None,
                                access_level_id=default_access_level.id)
        permission.save()

    def wrap_entity(self, external_object):
        """
        When the entity information is loaded from the external source, some external_object
        is created (e.g., a django.db.models.Model for database entity provider or dict for
        POSIX users provider). The goal of this function is to transform such external object
        to the entity.

        This method is called by the EntityReader and you are also free to call this method
        by the load_entity function.

        :param external_object: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        entity = super().wrap_entity(external_object)
        group_provider = GroupProvider()
        entity._root_group = group_provider.wrap_entity(entity._root_group)
        entity._governor = entity._root_group.governor
        return entity
