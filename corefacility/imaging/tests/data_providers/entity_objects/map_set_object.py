from core.entity.user import User
from core.entity.group import Group
from core.entity.project import Project
from core.test.entity_set.entity_set_objects.entity_set_object import EntitySetObject

from imaging.models.enums import MapType
from imaging.entity import Map


class MapSetObject(EntitySetObject):
    """
    Manages the map sets for testing purpose
    """

    _entity_class = Map

    _project1 = None
    _project2 = None

    @property
    def project1(self):
        return self._project1

    @property
    def project2(self):
        return self._project2

    def __init__(self, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function
        :param _entity_list: This is an internal argument. Don't use it.
        """
        if _entity_list is None:
            user = User(login="sergei_kozhukhov", name="Sergei", surname="Kozhukhov")
            user.create()
            group = Group(name="The Test Group", governor=user)
            group.create()
            self._project1 = Project(alias="project1", name="Project 1", root_group=group)
            self._project1.create()
            self._project2 = Project(alias="project2", name="Project 2", root_group=group)
            self._project2.create()
        super().__init__(_entity_list)

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        return [
            dict(alias="c022_X210", type=MapType.orientation, project=self.project1),
            dict(alias="c022_X100", type=MapType.direction, project=self.project1),
            dict(alias="c023_X2", type=MapType.orientation, project=self.project1),
            dict(alias="c025_X300", type=MapType.direction, project=self.project1),
            dict(alias="c040_X100", type=MapType.orientation, project=self.project2),
            dict(alias="c040_X101", type=MapType.direction, project=self.project2),
        ]
