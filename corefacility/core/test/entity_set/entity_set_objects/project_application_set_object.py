from core.entity.project_application import ProjectApplication
from imaging import App as ImagingApp
from roi import App as RoiApp

from .entity_set_object import EntitySetObject


class ProjectApplicationSetObject(EntitySetObject):
    """
    Defines the expected search result for the ProjectApplicationSet.
    """

    _entity_class = ProjectApplication
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    _alias_field = None
    """ The alias field. Override this class property is this is not true. """

    _project_set_object = None
    """ The child object: list of all objects that will be used during the project application set object creating """

    def __init__(self, project_set_object, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param _entity_list: This is an internal argument. Don't use it.
        """
        self._project_set_object = project_set_object
        super().__init__(_entity_list)

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        projects = self._project_set_object.entities
        return [
            dict(project=projects[6], application=ImagingApp(), is_enabled=True),
            dict(project=projects[6], application=RoiApp(), is_enabled=False),
            dict(project=projects[7], application=RoiApp(), is_enabled=True),
            dict(project=projects[7], application=ImagingApp(), is_enabled=False),
            dict(project=projects[8], application=RoiApp(), is_enabled=True),
            dict(project=projects[9], application=ImagingApp(), is_enabled=False),
            dict(project=projects[1], application=ImagingApp(), is_enabled=False),
            dict(project=projects[1], application=RoiApp(), is_enabled=True),
            dict(project=projects[2], application=RoiApp(), is_enabled=False),
            dict(project=projects[2], application=ImagingApp(), is_enabled=True),
            dict(project=projects[3], application=ImagingApp(), is_enabled=False),
            dict(project=projects[4], application=RoiApp(), is_enabled=True),
        ]

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._project_set_object.clone(), _entity_list=list(self._entities))

    def filter_by_entity_is_enabled(self, is_enabled):
        """
        Filters only application sets that met given conditions

        :param is_enabled: True to search among all enabled entities, False to search among all disabled entities
        :return: nothing
        """
        self._entities = list(filter(lambda entity: entity.is_enabled == is_enabled, self._entities))

    def filter_by_project(self, project):
        """
        Leaves only such expected search results that belong to a given project

        :param project: the project which search results shall belong to
        :return: nothing
        """
        self._entities = list(filter(lambda entity: entity.project.id == project.id, self._entities))

    def filter_by_application(self, app):
        """
        Leaves only such expected search results where given module is presented

        :param app: the application which search results shall belong to
        :return: nothing
        """
        self._entities = list(filter(lambda entity: entity.application.uuid == app.uuid, self._entities))

    def filter_by_application_is_enabled(self, is_enabled):
        """
        Leaves only such expected search results where given module is enabled

        :param is_enabled: True to search among all enabled entities, False otherwise
        :return: nothing
        """
        self._entities = list(filter(lambda entity: entity.application.is_enabled == is_enabled, self._entities))
