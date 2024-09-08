from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.labjournal_individual_options_provider import \
    LabjournalIndividualOptionsProvider
from ru.ihna.kozhukhov.core_application.models import LabjournalSearchProperties


class SearchPropertiesProvider(LabjournalIndividualOptionsProvider):
    """
    This class is responsible for information exchange between the SearchProperties instance and the database
    """

    _entity_model = LabjournalSearchProperties
    """ The Django model that manipulates the search properties information """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_search_properties.SearchProperties"
    """ Class of entities that this provider must create """

    def resolve_conflict(self, given_entity, contained_entity):
        """
        This function is called when the user tries to save the entity when another duplicated entity
        exists in this entity source.

        The aim of this function is to resolve the underlying conflict and probably call the
        'create_entity' function again

        :param given_entity: the entity the user tries to save
        :param contained_entity: the entity duplicate that has already been present on given entity source
        :return: nothing but must throw an exception when such entity can't be created
        """
        contained_entity.properties = given_entity.properties
        contained_entity.update()
        given_entity._id = contained_entity._id

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
        entity = super().wrap_entity(external_object)
        if hasattr(external_object, 'properties'):
            entity._properties = external_object.properties
        return entity

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        super()._unwrap_entity_properties(external_object, entity)
        external_object.properties = entity._properties

    def _get_lookup_object(self, entity):
        """
        Calculates the Django model that contains duplicates of throws the DoesNotExist exception if the entity
        has no duplicates

        :param entity: Entity which duplicates must be calculated
        :return: object with the same class as defined in the _entity_model property
        """
        return LabjournalSearchProperties.objects.get(
            project_id=entity.category.project.id,
            category_id=entity.category.id,
            user_id=entity.user.id,
        )
