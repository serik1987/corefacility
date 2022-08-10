from django.core.files import File
from core.entity.entity import Entity


class EntityProvider:
    """
    The entity provider is a connector between the entity and the underlying source that aids to
    completeness of several functions:

    1. Negotiation of uniformed entity API and a specific entity API of the underlying data source

    2. Each entity has several entity providers. When you try to save the entity all providers will
    be called sequentially. By this way they write uniformed information to all the sources keeping
    them up to date.

    3. The EntityProvider is responsible for 'wrapping' the entity: data conversion from the format
    suitable for certain data source to the entity format
    """

    def load_entity(self, entity: Entity):
        """
        The method checks that the entity has already been loaded from the database.
        EntityProviders shall use the entity 'id' or '_wrapped' properties of the corresponding
        entity.
        The entity 'id' field is a unique entity number given by the database system. The entity
        id doesn't relate to UID, GID or PID values given to entities by the Unix-like operating
        systems
        :param entity: the entity to load
        :return: the entity value
        """
        raise NotImplementedError("EntityProvider.load_entity is not implemented")

    def create_entity(self, entity: Entity):
        """
        Creates the entity in a certain entity source and changes the entity's _id and _wrapped properties
        according to how the entity changes its status
        :param entity: The entity to be created on this entity source
        :return: nothing but entity provider must fill necessary entity fields
        """
        raise NotImplementedError("EntityProvider.create_entity is not implemented")

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        """
        This function is called when the user tries to save the entity when another duplicated entity
        exists in this entity source.

        The aim of this function is to resolve the underlying conflict and probably call the
        'create_entity' function again

        :param given_entity: the entity the user tries to save
        :param contained_entity: the entity duplicate that has already been present on given entity source
        :return: nothing but must throw an exception when such entity can't be created
        """
        raise NotImplementedError("EntityProvider.resolve_conflict is not implemented")

    def update_entity(self, entity: Entity):
        """
        Updates the entity that has been already stored in the database

        :param entity: the entity to be updated
        :return: nothing
        """
        raise NotImplementedError("EntityProvider.update_entity is not implemented")

    def delete_entity(self, entity: Entity):
        """
        Deletes the entity from the external entity source

        :param entity: the entity to be deleted
        :return: nothing
        """
        raise NotImplementedError("EntityProvider.delete_entity is not implemented")

    def wrap_entity(self, external_object):
        """
        When the entity information is loaded from the external source, some external_object
        is created (e.g., a django.db.models.Model for database entity provider or dict for
        POSIX users provider). The goal of this function is to transform such external object
        to the entity.

        This method is called by the EntityReader and you are also free to call this method
        by the load_entity function.

        To create the entity using the wrap_entity method use the Entity constructor in the
        following way:
        entity = Entity(_src=external_object, field1=value1, field2=value2, ...)

        In this case,
        - the entity state will be 'loaded' rather then 'creating';
        - the entity _wrapped field will be assigned to this particular object

        :param external_object: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        raise NotImplementedError("EntityProvider.wrap_entity is not implemented")

    def unwrap_entity(self, entity: Entity):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        Nobody calls this function. You are free to call it from the delete_entity,
        create_entity or update_entity method as well as to leave this function non-implemented and
        write the conversion routines to these methods

        :param entity: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        raise NotImplementedError("EntityProvider.unwrap_entity is not implemented")

    def attach_file(self, entity: Entity, name: str, value: File) -> None:
        """
        Attaches a file to the entity representation located at external entity source

        :param entity: the entity to which the file can be attached
        :param name: the field name to which the file should be attached
        :param value: an instance of django.core.files.File object
        :return: nothing
        """
        raise NotImplementedError("EntityProvider.attach_file is not implemented")

    def detach_file(self, entity: Entity, name: str) -> None:
        """
        Detaches a file from the entity representation located at external entity source
        :param entity: the entity from which the file shall be detached
        :param name: the field name from which the file should be detached
        :return: nothing
        """
        raise NotImplementedError("EntityProvider.detach_file is not implemented")
