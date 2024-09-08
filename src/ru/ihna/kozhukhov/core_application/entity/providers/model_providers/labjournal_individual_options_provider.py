from django.utils.module_loading import import_string

from .model_provider import ModelProvider


class LabjournalIndividualOptionsProvider(ModelProvider):
    """
    This is the base class for the VieweParameterProvider and SearchPropertiesProvider both of which are
    used to set up individual user properties for each category.

    Their database table must contain 'project_id', 'category_id' and 'user_id' columns. Also, an individual
    implementation of the _unwrap_entity_properties and wrap_entity methods is also required
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
                lookup_object = self._get_lookup_object(entity)
                return self.wrap_entity(lookup_object)
            except self.entity_model.DoesNotExist:
                return None

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
        if hasattr(external_object, 'category'):
            create_kwargs['category'] = external_object.category
        if hasattr(external_object, 'user'):
            create_kwargs['user'] = external_object.user
        return self.entity_class(**create_kwargs)

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        if 'category' in entity._edited_fields:
            external_object.category_id = entity._category.id
            external_object.project_id = entity._category.project.id
        if 'user' in entity._edited_fields:
            external_object.user_id = entity._user.id

    def _get_lookup_object(self, entity):
        """
        Calculates the Django model that contains duplicates of throws the DoesNotExist exception if the entity
        has no duplicates

        :param entity: Entity which duplicates must be calculated
        :return: object with the same class as defined in the _entity_model property
        """
        raise NotImplementedError("_get_lookup_object")
