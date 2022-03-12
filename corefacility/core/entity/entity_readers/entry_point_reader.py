from core.models import EntryPoint
from .model_emulators import ModelEmulator
from .query_builders.data_source import SqlTable
from .query_builders.query_filters import StringQueryFilter

from .raw_sql_query_reader import RawSqlQueryReader
from ..entity_providers.model_providers.entry_point_provider import EntryPointProvider


class EntryPointReader(RawSqlQueryReader):
    """
    Reads the entry point information from the database and sends it to the EntryPointProvider
    """

    _entity_provider = EntryPointProvider()

    _lookup_table_name = "core_entrypoint"
    """
    Change this property if get() method will give you something like 'column ... is ambiguous'.
    This will make get() method to add 'WHERE tbl_name.id=%s' instead of 'WHERE id=%s'
    """

    _query_debug = True

    def initialize_query_builder(self):
        """
        Initializes items_builder and count_builder

        :return: nothing
        """
        self.items_builder\
            .add_select_expression("core_entrypoint.id")\
            .add_select_expression("core_entrypoint.entry_point_class")\
            .add_select_expression("core_entrypoint.alias")\
            .add_select_expression("core_entrypoint.type")\
            .add_select_expression("core_entrypoint.name")\
            .add_select_expression("belonging_module.app_class")\
            .add_order_term("core_entrypoint.name")

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count(""))

        for builder in (self.items_builder, self.count_builder):
            builder.add_data_source("core_entrypoint")
            builder.data_source.add_join(builder.JoinType.LEFT,
                                         SqlTable("core_module", "belonging_module"),
                                         "ON (belonging_module.uuid=belonging_module_id)")

    def apply_parent_module_is_root_filter(self, is_root):
        """
        Applies the parent module filter

        :param is_root: true if we want to seek only such entry points which parent modules are root. False if we
            need only such entry points which parent modules are not root
        :return: nothing
        """
        if is_root:
            query_filter = StringQueryFilter("belonging_module.parent_entry_point_id IS NULL")
        else:
            query_filter = StringQueryFilter("belonging_module.parent_entry_point_id IS NOT NULL")

        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= query_filter

    def apply_parent_module_filter(self, parent_module):
        """
        The parent module filter retrieves only entry points that belong to a given module

        :param parent_module: the module to which all entry points shall belong to
        :return: nothing
        """
        uuid = str(parent_module.uuid).replace('-', '')
        for builder in (self.items_builder, self.count_builder):
            builder.main_filter &= StringQueryFilter("belonging_module_id=%s", uuid)

    def create_external_object(self, entry_point_id, entry_point_class, alias, ep_type, name, belonging_module_class):
        return ModelEmulator(
            id=entry_point_id,
            entry_point_class=entry_point_class,
            alias=alias,
            type=ep_type,
            name=name,
            belonging_module_class=belonging_module_class
        )
