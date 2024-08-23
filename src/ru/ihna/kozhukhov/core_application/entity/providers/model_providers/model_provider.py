import os.path

from django.core.files import File
from django.db.utils import IntegrityError
from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityDuplicatedException
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

    @property
    def entity_model(self):
        """
        The entity model is a Django model that immediately stores information about the entity

        :return: the entity model
        """
        if isinstance(self._entity_model, str):
            self._entity_model = import_string(self._entity_model)
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
        try:
            entity_model = self.unwrap_entity(entity)
            entity_model.save()
            entity._id = entity_model.id
            entity._wrapped = entity_model
        except IntegrityError:
            raise EntityDuplicatedException()

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
        raise EntityDuplicatedException()

    def update_entity(self, entity: Entity):
        """
        Updates the entity that has been already stored in the database

        :param entity: the entity to be updated
        :return: nothing
        """
        try:
            entity_model = self.unwrap_entity(entity)
            entity_model.save()
        except IntegrityError:
            raise EntityDuplicatedException()

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
            if hasattr(external_object, field_name):
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
        if not isinstance(external_object, self.entity_model):
            external_object = self.entity_model.objects.get(pk=entity.id)  # + 1 EXTRA QUERY!
        self._unwrap_entity_properties(external_object, entity)
        return external_object

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        for field_name in self.model_fields:
            if field_name in entity._edited_fields:
                field_value = getattr(entity, '_' + field_name)
                if isinstance(field_value, Entity):
                    field_value = field_value._wrapped
                try:
                    setattr(external_object, field_name, field_value)
                except ValueError:
                    setattr(external_object, field_name + "_id", field_value.id)

    def attach_file(self, entity: Entity, name: str, value: File) -> None:
        """
        Attaches a file to the entity representation located at external entity source

        :param entity: the entity to which the file can be attached
        :param name: the field name to which the file should be attached
        :param value: an instance of django.core.files.File object
        :return: nothing
        """
        entity_model = entity._wrapped
        if not isinstance(entity_model, self.entity_model):
            entity_model = self.entity_model.objects.get(pk=entity.id)  # + 1 EXTRA QUERY!
        file_field = getattr(entity_model, name)
        _, ext = os.path.splitext(value.name)
        new_name = "%s_%s%s" % (entity.__class__.__name__.lower(), name, ext)
        file_field.save(new_name, value, save=True)
        setattr(entity, "_" + name, file_field)

    def detach_file(self, entity: Entity, name: str) -> None:
        """
        Detaches a file from the entity representation located at external entity source

        :param entity: the entity from which the file shall be detached
        :param name: the field name from which the file should be detached
        :return: nothing
        """
        entity_model = entity._wrapped
        if not isinstance(entity_model, self.entity_model):
            entity_model = self.entity_model.objects.get(pk=entity.id)  # + 1 EXTRA QUERY!
        field_value = getattr(entity_model, name)
        field_value.delete(save=True)
        setattr(entity, "_" + name, field_value)
