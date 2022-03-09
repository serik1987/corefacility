from core.entity.entity_providers.model_providers.model_provider import ModelProvider


class MapProvider(ModelProvider):
    """
    Exchanges information and control between the map entity and the map model
    """

    _entity_model = "imaging.models.Map"

    _lookup_field = "alias"

    _model_fields = ["alias", "data", "type", "resolution_x", "resolution_y", "width", "height"]

    _entity_class = "imaging.entity.Map"
