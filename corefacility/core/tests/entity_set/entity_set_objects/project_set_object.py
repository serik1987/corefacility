from core.entity.project import Project

from .entity_set_object import EntitySetObject
from .group_set_object import GroupSetObject


class ProjectSetObject(EntitySetObject):
    """
    Defines the project set immitation for testing purposes and giving expected results
    """

    MIN_GROUP_COUNT = 5

    __group_set_object = None
    """ All groups to set will be taken from this object """

    _entity_class = Project
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    def __init__(self, group_set_object: GroupSetObject, _entity_list=None):
        """
        Initializes new project set object, creates all projects implied by this set and stores them to the database

        :param group_set_object: The root group must be defined for each project. All groups will be taken
        from this group set (define at least five groups)
        """
        if len(group_set_object) < self.MIN_GROUP_COUNT:
            raise ValueError("ProjectSetObject.__init__: the group_set_object must contain at least %d groups" %
                             self.MIN_GROUP_COUNT)
        self.__group_set_object = group_set_object
        super().__init__(_entity_list=_entity_list)

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        g = self.__group_set_object
        return [
            dict(alias="nsw", name="Нейробиология сна и бодрствования", root_group=g[2]),  # 0
            dict(alias="n", name="Нейроонтогенез", root_group=g[3]),  # 1
            dict(alias="nl", name="Нейрофизиология обучения", root_group=g[3]),  # 2
            dict(alias="gcn", name="Общая и клиническая нейрофизиология", root_group=g[4]),  # 3
            dict(alias="aphhna", name="Прикладная физиология", root_group=g[4]),  # 4
            dict(alias="cr", name="Условные рефлексы", root_group=g[4]),  # 5
            dict(alias="hhna", name="Высшая нервная деятельность человека", root_group=g[0]),  # 6
            dict(alias="cnl", name="Клеточная нейробиология обучения", root_group=g[0]),  # 7
            dict(alias="mnl", name="Математическая нейробиология обучения", root_group=g[1]),  # 8
            dict(alias="mn", name="Молекулярная нейробиология", root_group=g[1]),  # 9
        ]

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return ProjectSetObject(self.__group_set_object, _entity_list=self._entities)

    def sort(self):
        """
        Sorts all project within the project set object according to their names.
        If you don't perform such an operation the iteration test and indexation test will be failed

        :return: nothing
        """
        self._entities = sorted(self._entities, key=lambda project: project.name)

    def filter_by_name(self, name):
        """
        Provides container filtration by the name

        :return: nothing
        """
        if isinstance(name, str) and str != "":
            self._entities = list(filter(lambda project: project.name.startswith(name), self._entities))
