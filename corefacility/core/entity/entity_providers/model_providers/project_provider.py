from core.models import Project, ProjectPermission
from .model_provider import ModelProvider
from .group_provider import GroupProvider


class ProjectProvider(ModelProvider):
    """
    Defines the project model provider. The project model provider allows storing projects on the database
    """

    _entity_model = Project
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = "alias"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = ["alias", "avatar", "name", "description", "root_group", "project_dir", "unix_group"]
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = "core.entity.project.Project"
    """
    Defines the entity class (the string notation)
    """

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
