from random import randrange

from core.test.entity_set.entity_set_objects.entity_set_object import EntitySetObject
from roi.entity import Pinwheel


class PinwheelSetObject(EntitySetObject):
    """
    Container for testing pinwheel centers
    """

    MAP_SIZE = 512

    PINWHEEL_NUMBER = 10

    _map_set_object = None

    _entity_class = Pinwheel

    def __init__(self, map_set_object, _entity_list=None):
        """
        Initializes the pinwheel set object

        :param map_set_object: set of the parent maps
        :param _entity_list: for service usage only
        """
        self._map_set_object = map_set_object
        super().__init__(_entity_list)

    def data_provider(self):
        """
        Provides the source data for construction of entities within the container

        :return: array of kwargs
        """
        kwargs_list = []
        for imaging_map in self._map_set_object.entities:
            for n in range(self.PINWHEEL_NUMBER):
                kwargs_list.append(dict(x=randrange(1, self.MAP_SIZE), y=randrange(1, self.MAP_SIZE), map=imaging_map))
        return kwargs_list

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._map_set_object, _entity_list=list(self._entities))

    def filter_by_map(self, imaging_map):
        """
        Leaves only such entities that belong to a given map

        :param imaging_map: the imaging map
        :return: nothing
        """
        self._entities = list(filter(lambda pinwheel: pinwheel.map.id == imaging_map.id, self._entities))
