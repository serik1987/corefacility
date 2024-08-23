from django.db import IntegrityError
from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.project_provider import ProjectProvider
from ru.ihna.kozhukhov.core_application.entity.project import Project
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityFieldInvalid
from ru.ihna.kozhukhov.core_application.models.labjournal_root_record import LabjournalRootRecord
from ru.ihna.kozhukhov.core_application.entity.providers.model_providers.model_provider import ModelProvider


class RootRecordProvider(ModelProvider):
    """
    Interacts between the root record and the LabjournalRootRecord table.
    Not suitable for any other types of records.
    """

    _model_fields = ['comments', 'base_directory']

    _entity_model = LabjournalRootRecord
    """ Defines a database table row where all information about the root category record stores """

    _entity_class = \
        "ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record.RootCategoryRecord"
    """ Defines the entity the this provider can wrap """

    def update_entity(self, root_record):
        """
        Updates the root record

        :param root_record: the root record to be updated
        """
        try:
            super().update_entity(root_record)
        except LabjournalRootRecord.DoesNotExist:
            entity_model = LabjournalRootRecord(project_id=root_record.project.id)
            for name in self.model_fields:
                if name in root_record._edited_fields:
                    value = getattr(root_record, name)
                    setattr(entity_model, name, value)
            try:
                entity_model.save()
            except IntegrityError:
                raise EntityFieldInvalid('base_directory')
            root_record._wrapped = entity_model

    def wrap_entity(self, external_object):
        """
        Transforms the external object to the root record

        :param external_object: the object to be transformed
        :return: The RootCategoryRecord instance
        """
        if isinstance(self._entity_class, str):
            self._entity_class = import_string(self._entity_class)
        root_record = self._entity_class(
            _src=external_object,
            id=None,
            comments=external_object.comments,
            base_directory=external_object.base_directory,
        )
        if hasattr(external_object, 'project'):
            project = external_object.project
            if not isinstance(project, Project):
                project = ProjectProvider().wrap_entity(project)
            root_record._project = project
        return root_record
