from core.entity.entity_sets.entity_set import EntitySet


class EntryPointSet(EntitySet):
    """
    Provides convenient interface that allows to find a proper entry point
    """

    _entity_name = "Entry Point"

    _entity_class = "core.entity.entry_points.EntryPoint"

    _entity_reader_class = "core.entity.entity_readers.entry_point_reader.EntryPointReader"

    _entity_filter_list = {
        "parent_module_is_root": (bool, None),
        "parent_module": ("core.entity.corefacility_module.CorefacilityModule", None),
    }
