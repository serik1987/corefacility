from core.entity.entity_providers.model_providers.model_provider import ModelProvider

from imaging.entity.map.map_provider import MapProvider


class RectangularRoiProvider(ModelProvider):
    """
    Exchanges information between the Django model layer and the RectangularRoi entity.
    """

    _entity_model = "roi.models.RectangularRoi"

    _lookup_field = "id"

    _model_fields = ["left", "right", "top", "bottom"]

    _entity_class = "roi.entity.RectangularRoi"

    _map_provider = MapProvider()

    def unwrap_entity(self, rectangular_roi):
        """
        Converts the RectangularRoi entity to the Django model. Such a model could be saved to the database.

        :param rectangular_roi: the entity to be converted
        :return: the Django model
        """
        roi_model = super().unwrap_entity(rectangular_roi)
        roi_model.map_id = rectangular_roi._map.id
        return roi_model

    def wrap_entity(self, external_object):
        """
        Converts external object to the rectangular ROI entity

        :param external_object: some object containing information loaded from the database
        :return: the RectangularRoi instance
        """
        rect_roi = super().wrap_entity(external_object)
        rect_roi._map = self._map_provider.wrap_entity(external_object.map)
        return rect_roi
