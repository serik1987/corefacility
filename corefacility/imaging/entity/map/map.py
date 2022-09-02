from core.entity.entity import Entity
from core.entity.entity_fields.related_entity_field import RelatedEntityField
from core.entity.entity_fields.choice_entity_field import ChoiceEntityField
from core.entity.entity_fields.float_field import FloatField
from core.entity.entity_fields.read_only_field import ReadOnlyField
from core.entity.entity_fields.entity_alias_field import EntityAliasField
from core.entity.entity_fields.managed_entity_field import ManagedEntityField
from core.entity.entity_fields.field_managers.public_file_manager import PublicFileManager

from .map_set import MapSet
from .map_provider import MapProvider


class Map(Entity):
    """
    This entity represents the imaging map
    """

    _entity_provider_list = [MapProvider()]

    _required_fields = ["alias", "type", "project"]

    _entity_set_class = MapSet
    
    _public_field_description = {
        "alias": EntityAliasField(max_length=50),
        "data": ManagedEntityField(PublicFileManager, "Imaging map file", include_media_root=False),
        "type": ChoiceEntityField("imaging.models.enums.MapType", description="Functional map type"),
        "resolution_x": ReadOnlyField(description="Map resolution, X"),
        "resolution_y": ReadOnlyField(description="Map resolution, Y"),
        "width": FloatField(min_value=0.0, min_value_included=False, description="Map width, um"),
        "height": FloatField(min_value=0.0, min_value_included=False, description="Map height, um"),
        "project": RelatedEntityField("core.entity.project.Project", description="Related project")
    }

    def __eq__(self, other):
        """
        Compares two functional maps (for debugging purpose only)

        :param other: the other functional map
        :return: nothing
        """
        if not isinstance(other, Map):
            return False
        if self.alias != other.alias:
            return False
        if self.data != other.data:
            return False
        if self.type != other.type:
            return False
        if self.resolution_x != other.resolution_x:
            return False
        if self.resolution_y != other.resolution_y:
            return False
        if self.width != other.width:
            return False
        if self.height != other.height:
            return False
        return True
