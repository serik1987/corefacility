from core.models import ProjectApplication as ProjectApplicationModel

from .model_provider import ModelProvider
from .corefacility_module_provider import CorefacilityModuleProvider
from .project_provider import ProjectProvider


class ProjectApplicationProvider(ModelProvider):
    """
    Exchanges the information between the ProjectApplication entity and the Django model layer
    """

    _entity_model = ProjectApplicationModel
    """ the entity model is a Django model that immediately stores information about the entity """

    _lookup_field = "id"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _model_fields = ["is_enabled"]
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = "core.entity.project_application.ProjectApplication"
    """
    Defines the entity class (the string notation)

    Use the string containing the class name, not class object (due to avoid cycling imports)
    """

    _module_provider = CorefacilityModuleProvider()

    _project_provider = ProjectProvider()

    def wrap_entity(self, source):
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

        :param source: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        project_application = super().wrap_entity(source)
        project_application._application = self._module_provider.wrap_entity(source.application)
        project_application._project = self._project_provider.wrap_entity(source.project)
        return project_application

    def unwrap_entity(self, project_application):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        :param project_application: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        source = super().unwrap_entity(project_application)
        source.application_id = project_application._application.uuid
        source.project_id = project_application._project.id
        return source
