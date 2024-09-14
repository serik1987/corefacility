from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags.hashtag_provider import HashtagProvider
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import DataRecord
from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.model_provider import ModelProvider
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.record_provider import RecordProvider
from ru.ihna.kozhukhov.core_application.models import LabjournalFile
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType


class FileProvider(ModelProvider):
    """
    Provides an information exchange between the corefacility File object and the database
    """

    _entity_model = LabjournalFile
    """ The Django model that relates to the entity"""

    _model_fields = ['record', 'name']
    """ Fields that have been stored in the database """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_file.File"
    """ Entities that shall be restored from information containing in the database """

    _record_provider = RecordProvider()
    """
    Transforms the external entity containing information about an experimental data record to the DataRecord instance
    """

    _hashtag_provider = HashtagProvider()
    """ Transforms the external entity containing information about a particular hashtag to the FileHashtag instance """

    _record_provider.current_type = LabjournalRecordType.data

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
                lookup_object = self.entity_model.objects.get(
                    name=entity.name,
                    record_id=entity.record.id,
                )
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
        entity = super().wrap_entity(external_object)
        if isinstance(external_object.record, DataRecord):
            entity._record = external_object.record
        else:
            entity._record = self._record_provider.wrap_entity(external_object.record)
        entity._update_path()
        if hasattr(external_object, 'hashtags'):
            entity._hashtags = [
                self._hashtag_provider.wrap_entity(hashtag_external_object)
                for hashtag_external_object in external_object.hashtags
            ]
        return entity
