from django.utils.module_loading import import_string

from core.entity.entity import Entity
from ..entity_provider import EntityProvider


class ModelProvider(EntityProvider):
    """
    The model entity providers are such providers that use Django models to store the data
    """

    _entity_model = None
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = None
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = None
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = None
    """
    Defines the entity class (the string notation)
    
    Use the string containing the class name, not class object (due to avoid cycling imports)
    """

    def load_entity(self, entity):
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
        if entity.id is not None or entity._wrapped is not None:
            return entity
        else:
            try:
                lookup_value = getattr(entity, self.lookup_field)
                lookup_object = self.entity_model.objects.get(**{self.lookup_field: lookup_value})
                return self.wrap_entity(lookup_object)
            except self.entity_model.DoesNotExist:
                return None

    def create_entity(self, entity):
        """
        Creates the entity in a certain entity source and changes the entity's _id and _wrapped properties
        according to how the entity changes its status.

        :param entity: The entity to be created on this entity source
        :return: nothing but entity provider must fill necessary entity fields
        """
        entity_model = self.unwrap_entity(entity)
        entity_model.save()
        entity._id = entity_model.id
        entity._wrapped = entity_model

    def update_entity(self, entity: Entity):
        """
        Updates the entity that has been already stored in the database

        :param entity: the entity to be updated
        :return: nothing
        """
        entity_model = self.unwrap_entity(entity)
        entity_model.save()

    def delete_entity(self, entity: Entity):
        """
        Deletes the entity from the external entity source

        :param entity: the entity to be deleted
        :return: nothing
        """
        entity_model = self.unwrap_entity(entity)
        entity_model.delete()

    def wrap_entity(self, external_object):
        """
        When the entity information is loaded from the external source, some external_object
        is created (e.g., a django.db.models.Model for database entity provider or dict for
        POSIX users provider). The goal of this function is to transform such external object
        to the entity.

        This method is called by the EntityReader and you are also free to call this method
        by the load_entity function.

        The wrap_entity doesn't retrieve all fields correctly. This is the main and only main
        reason why EntityProvider and EntityReader doesn't want to retrieve the same fields it saved
        and why test_object_created_updated_and_loaded_default and test_object_created_and_loaded
        test cases fail with AssertionError. However, you can override this method in the inherited
        class in such a way as it retrieves all the fields correctly.

        :param external_object: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        if isinstance(self._entity_class, str):
            self._entity_class = import_string(self._entity_class)
        create_kwargs = {"_src": external_object, "id": external_object.id}
        for field_name in self.model_fields:
            field_value = getattr(external_object, field_name)
            create_kwargs[field_name] = field_value
        return self.entity_class(**create_kwargs)

    def unwrap_entity(self, entity):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        :param entity: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        if entity.state == "creating":
            external_object = self.entity_model()
        else:
            external_object = entity._wrapped
        if isinstance(external_object, dict):
            external_object = self.entity_model.objects.get(pk=entity.id)
            entity._wrapped = external_object
        for field_name in self.model_fields:
            if field_name in entity._edited_fields:
                field_value = getattr(entity, '_' + field_name)
                if isinstance(field_value, Entity):
                    field_value = field_value._wrapped
                setattr(external_object, field_name, field_value)
        return external_object

    @property
    def entity_model(self):
        """
        The entity model is a Django model that immediately stores information about the entity

        :return: the entity model
        """
        if self._entity_model is None:
            raise NotImplementedError("ModelProvider._entity_model: the class property is not defines")
        else:
            return self._entity_model

    @property
    def lookup_field(self):
        """
        The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
        database.

        :return: the lookup field
        """
        if self._lookup_field is None:
            raise NotImplementedError("ModelProvider._lookup_field: the class property is not defined")
        else:
            return self._lookup_field

    @property
    def model_fields(self):
        """
        Defines fields in the entity object that shall be stored as Django model

        :return: the model fields
        """
        if self._model_fields is None:
            raise NotImplementedError("ModelProvider._model_fields: the class property is not defined")
        else:
            return self._model_fields

    @property
    def entity_class(self):
        """
        Defines the entity class (the string notation)
        """
        if self._entity_class is None:
            raise NotImplementedError("ModelProvider._entity_class: the class property is not defined")
        else:
            return self._entity_class
