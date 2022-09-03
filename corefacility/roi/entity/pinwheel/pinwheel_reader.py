from core.entity.entity_readers.raw_sql_query_reader import RawSqlQueryReader
from core.entity.entity_readers.query_builders.query_filters import StringQueryFilter
from core.entity.entity_readers.model_emulators import ModelEmulator, ModelEmulatorFileField

from .pinwheel_provider import PinwheelProvider


class PinwheelReader(RawSqlQueryReader):
    """
    Retireves information about pinwheel centers from the database and passes it to the Pinwheel entity
    """

    _entity_provider = PinwheelProvider()

    _query_debug = False

    _lookup_table_name = "roi_pinwheel"

    def initialize_query_builder(self):
        """
        Constructs an initial query

        :return: nothing
        """
        for builder in (self.items_builder, self.count_builder):
            builder.add_data_source("roi_pinwheel")
            builder.data_source.add_join(self.items_builder.JoinType.INNER, "imaging_map",
                                         "ON (imaging_map.id=roi_pinwheel.map_id)")

        self.count_builder.add_select_expression(self.count_builder.select_total_count())

        self.items_builder \
            .add_select_expression("roi_pinwheel.id") \
            .add_select_expression("roi_pinwheel.x") \
            .add_select_expression("roi_pinwheel.y") \
            .add_select_expression("imaging_map.id") \
            .add_select_expression("imaging_map.alias") \
            .add_select_expression("imaging_map.data") \
            .add_select_expression("imaging_map.type") \
            .add_select_expression("imaging_map.resolution_x") \
            .add_select_expression("imaging_map.resolution_y") \
            .add_select_expression("imaging_map.width") \
            .add_select_expression("imaging_map.height") \
            .add_select_expression("imaging_map.project_id") \
            .add_order_term("roi_pinwheel.id")

    def apply_map_filter(self, imaging_map):
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("imaging_map.id=%s", imaging_map.id)

    def apply_map_id_filter(self, map_id):
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("imaging_map.id=%s", map_id)

    def apply_map_alias_filter(self, map_alias):
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("imaging_map.alias=%s", map_alias)

    def apply_project_id_filter(self, project_id):
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("imaging_map.project_id=%s", project_id)

    def create_external_object(self, pinwheel_id, pinwheel_x, pinwheel_y, map_id, map_alias, map_data, map_type,
                               map_resolution_x, map_resolution_y, map_width, map_height, project_id=None):
        from imaging.models.enums import MapType
        return ModelEmulator(
            id=pinwheel_id,
            x=pinwheel_x,
            y=pinwheel_y,
            map=ModelEmulator(
                id=map_id,
                alias=map_alias,
                data=ModelEmulatorFileField(name=map_data),
                type=MapType(map_type),
                resolution_x=map_resolution_x,
                resolution_y=map_resolution_y,
                width=map_width,
                height=map_height,
                project_id=project_id
            )
        )
