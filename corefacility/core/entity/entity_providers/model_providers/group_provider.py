from django.db.models import Model
from core.models import Group, GroupUser
from .model_provider import ModelProvider
from .user_provider import UserProvider
from ...entity import Entity
from ...entity_exceptions import EntityFieldInvalid


class GroupProvider(ModelProvider):
    """
    Provides facilities for storing groups to the database
    """

    _entity_model = Group
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = "name"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = ["name"]
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = "core.entity.group.Group"
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
        governor_model = GroupUser(group_id=entity.id, user_id=entity.governor.id, is_governor=True)
        governor_model.save()

    def update_entity(self, entity: Entity):
        """
        Updates the entity that has been already stored in the database

        :param entity: the entity to be updated
        :return: nothing
        """
        super().update_entity(entity)
        if "governor" in entity._edited_fields:
            all_users = GroupUser.objects.filter(group_id=entity.id)
            try:
                new_governor = all_users.get(user_id=entity._governor.id)
            except GroupUser.DoesNotExist:
                raise EntityFieldInvalid("governor [user exists but not in group]")
            all_users.update(is_governor=False)
            new_governor.is_governor = True
            new_governor.save()

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
        if hasattr(external_object, "governor"):
            governor_object = external_object.governor
        else:
            governor_object = \
                GroupUser.objects.get(group_id=external_object.id, is_governor=True).user  # +2 EXTRA QUERIES!
        governor_provider = UserProvider()
        governor = governor_provider.wrap_entity(governor_object)
        entity._governor = governor
        return entity
