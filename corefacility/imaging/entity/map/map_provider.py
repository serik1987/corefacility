from core.entity.entity_providers.model_providers.project_data_provider import ProjectDataProvider
from core.entity.entity_readers.model_emulators import ModelEmulator


class MapProvider(ProjectDataProvider):
    """
    Exchanges information and control between the map entity and the map model
    """

    _entity_model = "imaging.models.Map"

    _lookup_field = "alias"

    _model_fields = ["alias", "data", "type", "resolution_x", "resolution_y", "width", "height", "project"]

    _entity_class = "imaging.entity.Map"

    def wrap_entity(self, map_model):
        """
        Transforms functional map from the model representation to the entity representation
        :param map_model: the model representation
        :return: the entity representation
        """
        from core.entity.project import Project
        external_object = ModelEmulator(
            id=map_model.id,
            alias=map_model.alias,
            type=map_model.type,
            data=map_model.data,
            resolution_x=map_model.resolution_x,
            resolution_y=map_model.resolution_y,
            width=map_model.width,
            height=map_model.height
        )
        functional_map = super().wrap_entity(external_object)
        external_project_object = ModelEmulator(id=map_model.project_id)
        project = Project(_src=external_project_object, id=map_model.project_id)
        functional_map._project = project
        return functional_map
