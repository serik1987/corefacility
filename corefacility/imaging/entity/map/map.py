from core.entity.entity import Entity
from core.entity.entity_fields import EntityField
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

    _required_fields = ["alias", "type"]

    _entity_set_class = MapSet
    
    _public_field_description = {
        "alias": EntityAliasField(max_length=50),
        "data": ManagedEntityField(PublicFileManager, "Imaging map file"),
        "type": ChoiceEntityField("imaging.models.enums.MapType", description="Functional map type"),
        "resolution_x": ReadOnlyField(description="Map resolution, X"),
        "resolution_y": ReadOnlyField(description="Map resolution, Y"),
        "width": FloatField(min_value=0.0, min_value_included=False, description="Map width, um"),
        "height": FloatField(min_value=0.0, min_value_included=False, description="Map height, um"),
    }
