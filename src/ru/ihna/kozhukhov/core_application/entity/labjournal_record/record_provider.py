from datetime import datetime

from django.db import IntegrityError
from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.project_provider import ProjectProvider
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityDuplicatedException, \
    EntityFieldInvalid
from ru.ihna.kozhukhov.core_application.models.labjournal_record import LabjournalRecord as RecordModel
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.model_provider import ModelProvider


class RecordProvider(ModelProvider):
    """
    Provides interaction between the Record entity and the LabjournalRecord model.

    Not suitable for the root record.
    """

    _entity_model = RecordModel

    _current_type = None
    """ Considering type of the entity """

    _model_fields_dictionary = {
        'D': ['parent_category', 'project', 'level', 'alias', 'datetime', 'type', 'comments',],
        'S': ['parent_category', 'project', 'level', 'datetime', 'type', 'comments', 'name',],
        'C': ['parent_category', 'project', 'level', 'alias', 'datetime', 'type', 'comments',
              'finish_time', 'base_directory'],
    }
    """ A dictionary where we shall put necessary model fields """

    _entity_class_dictionary = {
        'D': "ru.ihna.kozhukhov.core_application.entity.labjournal_record.data_record.DataRecord",
        'S': "ru.ihna.kozhukhov.core_application.entity.labjournal_record.service_record.ServiceRecord",
        'C': "ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record.CategoryRecord",
    }

    @property
    def model_fields(self):
        """
        Defines fields in the entity object that shall be stored as Django model

        :return: the model fields
        """
        if self._current_type is None:
            raise RuntimeError("model_fields is not accessible because _current_type was not set")
        else:
            return self._model_fields_dictionary[self._current_type]

    @property
    def entity_class(self):
        """
        Defines the entity class (the string notation)
        """
        if self._current_type is None:
            raise RuntimeError("entity_class is not accessible because _current_type was not set")
        else:
            if isinstance(self._entity_class_dictionary[self._current_type], str):
                self._entity_class_dictionary[self._current_type] = \
                    import_string(self._entity_class_dictionary[self._current_type])
            return self._entity_class_dictionary[self._current_type]

    @property
    def current_type(self):
        """
        At a given time the EntityProvider is able to deal with a given particular type of laboratory record
        """
        return self._current_type

    @current_type.setter
    def current_type(self, value):
        self._current_type = value

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
        another_entity = None
        self._current_type = str(entity.type)
        if entity._type != LabjournalRecordType.service:
            # This is because service record is the only record that has no record alias and has no duplicated records
            try:
                lookup_object = RecordModel.objects.get(
                    project=entity._project.id,
                    parent_category_id=entity._parent_category.id,
                    alias=entity._alias
                )
                another_entity = self.wrap_entity(lookup_object)
            except RecordModel.DoesNotExist:
                pass
        self._current_type = None
        return another_entity

    def create_entity(self, entity):
        """
        Creates the entity in a certain entity source and changes the entity's _id and _wrapped properties
        according to how the entity changes its status.

        :param entity: The entity to be created on this entity source
        :return: nothing but entity provider must fill necessary entity fields
        """
        try:
            self._current_type = entity.type
            entity_model = self.unwrap_entity(entity)
            if self._duplicates_exists(entity):
                raise EntityDuplicatedException()
            entity_model.type = entity.type
            entity_model.save()
            entity._id = entity_model.id
            entity._wrapped = entity_model
            self._current_type = None
        except IntegrityError:
            raise EntityDuplicatedException()

    def update_entity(self, entity):
        """
        Updates the entity that has been already stored in the database

        :param entity: the entity to be updated
        :return: nothing
        """
        try:
            self._current_type = str(entity.type)
            entity_model = self.unwrap_entity(entity)
            if self._duplicates_exists(entity):
                raise EntityFieldInvalid('alias')
            entity_model.save()
            self._current_type = None
        except IntegrityError:
            raise EntityDuplicatedException()

    def delete_entity(self, entity):
        """
        Deletes the entity from the external entity source

        :param entity: the entity to be deleted
        :return: nothing
        """
        self._current_type = str(entity.type)
        super().delete_entity(entity)
        self._current_type = None

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
        from .category_record import CategoryRecord
        from .root_category_record import RootCategoryRecord
        entity = super().wrap_entity(external_object)
        entity._project = ProjectProvider().wrap_entity(entity._project)
        if external_object.parent_category_id is None:
            entity._parent_category = RootCategoryRecord(project=entity._project)
        else:
            entity._parent_category = CategoryRecord(
                _src=entity._parent_category,
                id=external_object.parent_category_id,
                datetime=external_object.parent_category.datetime,
                finish_time=external_object.parent_category.finish_time,
                project=entity.project,
            )
        if external_object.parent_category is not None and \
                isinstance(external_object.parent_category, ModelEmulator) and \
                isinstance(external_object.parent_category.datetime, datetime) and \
                isinstance(external_object.datetime, datetime):
            entity._relative_time = external_object.datetime - external_object.parent_category.datetime
        if hasattr(external_object, 'user'):
            entity._user = external_object.user
        if hasattr(external_object, 'checked'):
            entity._checked = external_object.checked
        return entity

    def _unwrap_entity_properties(self, external_object, entity):
        """
        Copies all entity properties from the entity object to the external_object

        :param external_object: Destination of the properties
        :param entity: Source of the properties
        """
        super()._unwrap_entity_properties(external_object, entity)
        external_object.parent_category_id = entity.parent_category.id

    def _duplicates_exists(self, entity):
        """
        Checks whether the parent category contains another entities with the same alias.

        :param entity: the entity which alias is required to be checked
        :return: True if such entities exists, False if either such entities doesn't exist or the entity is a service
            record (the uniqueness requirements shall not be satisfied for the service records) or 'alias' field
            doesn't changed by the view layer
        """
        duplicates_exist = False
        if entity.type != LabjournalRecordType.service and \
                ('alias' in entity._edited_fields or 'parent_category' in entity._edited_fields):
            lookup_objects = RecordModel.objects.filter(
                project_id=entity._project.id,
                parent_category_id=entity._parent_category.id,
                alias=entity._alias,
            ).exclude(type=LabjournalRecordType.service)
            if len(lookup_objects) > 1 or \
                    (len(lookup_objects) == 1 and lookup_objects[0].id != entity.id):
                duplicates_exist = True
        return duplicates_exist
