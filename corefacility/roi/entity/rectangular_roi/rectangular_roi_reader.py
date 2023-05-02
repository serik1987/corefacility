from core.entity.entity_readers.raw_sql_query_reader import RawSqlQueryReader
from core.entity.entity_readers.query_builders.query_filters import StringQueryFilter
from core.entity.entity_readers.model_emulators import ModelEmulator, ModelEmulatorFileField

from .rectangular_roi_provider import RectangularRoiProvider


class RectangularRoiReader(RawSqlQueryReader):
    """
    Finds information about a given rectangular ROI from the database and sends it to the ROI provider
    """

    _entity_provider = RectangularRoiProvider()

    _lookup_table_name = "roi_rectangularroi"

    def initialize_query_builder(self):
        for builder in (self.items_builder, self.count_builder):
            builder.add_data_source("roi_rectangularroi")
            builder.data_source.add_join(builder.JoinType.INNER, "imaging_map",
                                         "ON (imaging_map.id=roi_rectangularroi.map_id)")

        self.count_builder.add_select_expression(self.count_builder.select_total_count())

        self.items_builder \
            .add_select_expression("roi_rectangularroi.id") \
            .add_select_expression("roi_rectangularroi.left") \
            .add_select_expression("roi_rectangularroi.right") \
            .add_select_expression("roi_rectangularroi.top") \
            .add_select_expression("roi_rectangularroi.bottom") \
            .add_select_expression("imaging_map.id") \
            .add_select_expression("imaging_map.alias") \
            .add_select_expression("imaging_map.data") \
            .add_select_expression("imaging_map.type") \
            .add_select_expression("imaging_map.resolution_x") \
            .add_select_expression("imaging_map.resolution_y") \
            .add_select_expression("imaging_map.width") \
            .add_select_expression("imaging_map.height") \
            .add_select_expression("imaging_map.project_id") \
            .add_order_term("roi_rectangularroi.id")

    def apply_map_filter(self, imaging_map):
        for builder in (self.count_builder, self.items_builder):
            builder.main_filter &= StringQueryFilter("imaging_map.id=%s", imaging_map.id)

    def create_external_object(self, roi_id, roi_left, roi_right, roi_top, roi_bottom,
                               map_id, map_alias, map_data, map_type, resolution_x, resolution_y, width, height,
                               project_id):
        from imaging.models.enums import MapType
        return ModelEmulator(
            id=roi_id,
            left=roi_left,
            right=roi_right,
            top=roi_top,
            bottom=roi_bottom,
            map=ModelEmulator(
                id=map_id,
                alias=map_alias,
                data=ModelEmulatorFileField(name=map_data),
                type=MapType(map_type),
                resolution_x=resolution_x,
                resolution_y=resolution_y,
                width=width,
                height=height,
                project_id=project_id
            )
        )
