from random import randint

from core.test.entity_set.entity_set_objects.entity_set_object import EntitySetObject
from roi.entity import RectangularRoi


class RectangularRoiSetObject(EntitySetObject):
    """
    Represents a container where testing ROIs may be represented
    """

    _entity_class = RectangularRoi

    _map_set_object = None

    ROI_NUMBER = 5

    def __init__(self, map_set_object, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param map_set_object: The parent map set object
        :param _entity_list: This is an internal argument. Don't use it.
        """
        self._map_set_object = map_set_object
        super().__init__(_entity_list)

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        return [
            dict(left=randint(1, 512), right=randint(1, 512), top=randint(1, 512), bottom=randint(1, 512),
                 map=current_map)
            for n in range(self.ROI_NUMBER)
            for current_map in self._map_set_object
        ]

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._map_set_object.clone(), _entity_list=list(self._entities))

    def filter_by_map(self, imaging_map):
        """
        Destroys all ROIs within the container that does NOT belong to a given map

        :param imaging_map: a given map
        :return: nothing
        """
        self._entities = list(filter(lambda roi: roi.map.id == imaging_map.id, self._entities))
