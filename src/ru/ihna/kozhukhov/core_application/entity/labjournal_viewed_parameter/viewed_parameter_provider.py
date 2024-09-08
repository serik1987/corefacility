from django.db import models
from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.models import LabjournalParameterView
from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.labjournal_individual_options_provider import \
    LabjournalIndividualOptionsProvider

from ..labjournal_parameter_descriptor.parameter_descriptor_provider import ParameterDescriptorProvider


class ViewedParameterProvider(LabjournalIndividualOptionsProvider):
    """
    Provides data interaction between the ViewedParameter object and the database
    """

    _entity_model = LabjournalParameterView
    """ The Django model that is used for storage/retrieval information in the database """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_viewed_parameter.ViewedParameter"
    """ Class of the entities that this provider has to construct """

    _descriptor_provider = ParameterDescriptorProvider()
    """ A provider that is used to wrap a child parameter descriptor """

    def delete_entity(self, entity):
        """
        Deletes the entity from the external entity source

        :param entity: the entity to be deleted
        :return: nothing
        """
        super().delete_entity(entity)
        remaining_models = list(LabjournalParameterView.objects.filter(
            project_id=entity.category.project.id,
            category_id=entity.category.id,
            user_id=entity.user.id,
        ).order_by('index'))
        if len(remaining_models) > 0:
            for index, model in enumerate(remaining_models):
                model.index = index+1
            LabjournalParameterView.objects.bulk_update(remaining_models, ['index'])

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
        if hasattr(external_object, 'descriptor'):
            entity._descriptor = self._descriptor_provider.wrap_entity(external_object.descriptor)
        if hasattr(external_object, 'index'):
            entity._index = external_object.index
        return entity

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        super()._unwrap_entity_properties(external_object, entity)
        if 'index' in entity._edited_fields:
            external_object.index = entity._index
        if external_object.index is None:
            max_index = LabjournalParameterView.objects\
                .filter(
                    project_id=entity.category.project.id,
                    category_id=entity.category.id,
                    user_id=entity.user.id,
                ) \
                .aggregate(max_index=models.Max('index'))['max_index']
            if max_index is None:  #No items stored
                external_object.index = 1
            else:
                external_object.index = max_index+1
            entity._index = external_object.index
        if 'descriptor' in entity._edited_fields:
            external_object.descriptor_id = entity._descriptor.id

    def _get_lookup_object(self, entity):
        """
        Calculates the Django model that contains duplicates of throws the DoesNotExist exception if the entity
        has no duplicates

        :param entity: Entity which duplicates must be calculated
        :return: object with the same class as defined in the _entity_model property
        """
        return LabjournalParameterView.objects.get(
            project_id=entity.category.project.id,
            category_id=entity.category.id,
            user_id=entity.user.id,
            descriptor_id=entity.descriptor.id,
        )
