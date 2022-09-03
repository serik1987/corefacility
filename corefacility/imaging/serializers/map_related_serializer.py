from rest_framework.exceptions import NotFound

from core.entity.entity_exceptions import EntityNotFoundException
from core.serializers import EntitySerializer
from imaging.entity import MapSet


class MapRelatedSerializer(EntitySerializer):
    """
    Base class that can provide serialization and deserialization of all entities which mandatory argument is
    'map' which means functional map the entity shall be attached to
    """

    def create(self, data):
        """
        Creates a pinwheel from the data
        :param data: data from which the pinwheel must be created
        :return: nothing
        """
        map_lookup = self.context['view'].kwargs['map_lookup']
        try:
            map_lookup = int(map_lookup)
        except ValueError:
            pass
        try:
            map_set = MapSet()
            map_set.project = self.context['request'].project
            functional_map = map_set.get(map_lookup)
        except EntityNotFoundException:
            raise NotFound()
        data["map"] = functional_map
        return super().create(data)
