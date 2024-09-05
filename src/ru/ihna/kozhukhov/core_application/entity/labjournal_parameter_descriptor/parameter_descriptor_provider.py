from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.model_provider import ModelProvider
from ru.ihna.kozhukhov.core_application.models import LabjournalParameterDescriptor
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_field_type import LabjournalFieldType
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityOperationNotPermitted


class ParameterDescriptorProvider(ModelProvider):
    """
    Provides an information exchange between the ParameterDescriptor class
    """

    _entity_model = LabjournalParameterDescriptor
    _lookup_field = None
    _model_fields = ['identifier', 'description', 'required', 'default']
    _entity_class = None

    _current_type = None
    """ Represents current type for the entity """

    _entity_class_prefix = "ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor"
    _entity_class_list = {
        'B': _entity_class_prefix + ".boolean_parameter_descriptor.BooleanParameterDescriptor",
        'N': _entity_class_prefix + ".number_parameter_descriptor.NumberParameterDescriptor",
        'S': _entity_class_prefix + ".string_parameter_descriptor.StringParameterDescriptor",
        'D': _entity_class_prefix + ".discrete_parameter_descriptor.DiscreteParameterDescriptor",
    }

    @property
    def entity_class(self):
        """
        Defines the entity class (the string notation)
        """
        if self._current_type is None:
            raise RuntimeError("The _current_type hidden field was not set")
        entity_class = self._entity_class_list[self._current_type]
        if isinstance(entity_class, str):
            entity_class = import_string(entity_class)
            self._entity_class_list[self._current_type] = entity_class
        return entity_class

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
        if entity.id is not None and entity._wrapped is not None:
            return entity
        else:
            try:
                lookup_object = self.entity_model.objects.get(
                    project_id=entity.category.project.id,
                    identifier=entity.identifier
                )
                return self.wrap_entity(lookup_object)
            except self.entity_model.DoesNotExist:
                return None

    def update_entity(self, entity):
        """
        Updates the entity that has been already stored in the database

        :param entity: the entity to be updated
        :return: nothing
        """
        if 'category' in entity._edited_fields:
            raise EntityOperationNotPermitted()
        super().update_entity(entity)

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
        self._current_type = external_object.type
        entity = super().wrap_entity(external_object)
        self._current_type = None
        entity._category = external_object.category
        entity._index = external_object.index
        if hasattr(external_object, 'record_type'):
            entity._record_type = external_object.record_type
        else:
            entity._record_type = list()
            if external_object.for_data_record:
                entity._record_type.append(LabjournalRecordType.data)
            if external_object.for_service_record:
                entity._record_type.append(LabjournalRecordType.service)
            if external_object.for_category_record:
                entity._record_type.append(LabjournalRecordType.category)
        if entity.type == LabjournalFieldType.number:
            entity._units = external_object.units
        if entity.type == LabjournalFieldType.discrete:
            if hasattr(external_object, 'values'):
                entity._values = external_object.values
            else:
                entity._values = list()
        return entity

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        super()._unwrap_entity_properties(external_object, entity)
        if entity.state == 'creating':
            external_object.category_id = entity.category.id
            external_object.project_id = entity.category.project.id
            """
            external_object.index = self.entity_model.objects.filter(
                category_id=entity.category.id,
                project_id=entity.category.project.id,
            ) \
                .aggregate(Max('index'))['index__max']
            if external_object.index is None:
                external_object.index = 1
            else:
                external_object.index += 1
            """
            external_object.type = entity.type
        external_object.for_data_record = LabjournalRecordType.data in entity._record_type
        external_object.for_service_record = LabjournalRecordType.service in entity._record_type
        external_object.for_category_record = LabjournalRecordType.category in entity._record_type
        if entity.type == LabjournalFieldType.number:
            external_object.units = entity._units
        return external_object
