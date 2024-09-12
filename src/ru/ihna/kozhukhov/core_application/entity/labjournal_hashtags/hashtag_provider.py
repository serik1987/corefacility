from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.model_provider import ModelProvider
from ru.ihna.kozhukhov.core_application.models import LabjournalHashtag
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType


class HashtagProvider(ModelProvider):
    """
    Provides an information exchange between the Hashtag entity and the database
    """

    _entity_model = LabjournalHashtag
    """ Django database model that is responsible for information store/retrieval to/from the database """

    _model_fields = ['description', 'project', 'type']
    """ Entity fields that are stored within the database """

    _labjournal_hashtag_classes = {
        LabjournalHashtagType.record: "ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags.RecordHashtag",
        LabjournalHashtagType.file: "ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags.FileHashtag",
    }

    def get_entity_class_for_type(self, hashtag_type: LabjournalHashtagType):
        """
        Choices a proper hashtag class that relates to a given hashtag type

        :param hashtag_type: a hashtag type to use
        :return: a class that must be used to create the hashtag
        """
        if isinstance(self._labjournal_hashtag_classes[hashtag_type], str):
            self._labjournal_hashtag_classes[hashtag_type] = \
                import_string(self._labjournal_hashtag_classes[hashtag_type])
        return self._labjournal_hashtag_classes[hashtag_type]

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
                lookup_object = LabjournalHashtag.objects.get(
                    project_id=entity.project.id,
                    type=entity.type,
                    description=entity.description,
                )
                return self.wrap_entity(lookup_object)
            except LabjournalHashtag.DoesNotExist:
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
        return self.get_entity_class_for_type(external_object.type)(
            _src=external_object,
            id=external_object.id,
            description=external_object.description,
            project=external_object.project,
        )

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        super()._unwrap_entity_properties(external_object, entity)
        external_object.type = entity._type
