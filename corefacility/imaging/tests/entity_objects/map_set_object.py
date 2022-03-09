from core.test.entity_set.entity_set_objects.entity_set_object import EntitySetObject
from imaging.models.enums import MapType
from imaging.entity import Map


class MapSetObject(EntitySetObject):
    """
    Manages the map sets for testing purpose
    """

    _entity_class = Map

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        return [
            dict(alias="c022_X210", type=MapType.orientation),
            dict(alias="c022_X100", type=MapType.direction),
            dict(alias="c023_X2", type=MapType.orientation),
            dict(alias="c025_X300", type=MapType.direction),
            dict(alias="c040_X100", type=MapType.orientation),
            dict(alias="c040_X101", type=MapType.direction),
        ]
