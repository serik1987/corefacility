from django.db import models
from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.models import LabjournalParameterView

from ..providers.model_providers.model_provider import ModelProvider
from ..labjournal_parameter_descriptor.parameter_descriptor_provider import ParameterDescriptorProvider


class ViewedParameterProvider(ModelProvider):
    """
    Provides data interaction between the ViewedParameter object and the database
    """

    _entity_model = LabjournalParameterView
    """ The Django model that is used for storage/retrieval information in the database """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_viewed_parameter.ViewedParameter"
    """ Class of the entities that this provider has to construct """

    _descriptor_provider = ParameterDescriptorProvider()
    """ A provider that is used to wrap a child parameter descriptor """

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
                lookup_object = LabjournalParameterView.objects.get(
                    project_id=entity.category.project.id,
                    category_id=entity.category.id,
                    user_id=entity.user.id,
                    descriptor_id=entity.descriptor.id,
                )
                return self.wrap_entity(lookup_object)
            except self.entity_model.DoesNotExist:
                return None

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
        if isinstance(self._entity_class, str):
            self._entity_class = import_string(self._entity_class)
        create_kwargs = {"_src": external_object, "id": external_object.id}
        if hasattr(external_object, 'index'):
            create_kwargs['index'] = external_object.index
        if hasattr(external_object, 'descriptor'):
            create_kwargs['descriptor'] = self._descriptor_provider.wrap_entity(external_object.descriptor)
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
        if 'category' in entity._edited_fields:
            external_object.category_id = entity._category.id
            external_object.project_id = entity._category.project.id
        if 'user' in entity._edited_fields:
            external_object.user_id = entity._user.id
