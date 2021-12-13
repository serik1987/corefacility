from core.entity.entity_sets.entity_set import EntitySet


class EntryPointSet(EntitySet):
    """
    Provides convenient interface that allows to find a proper entry point
    """

    _entity_name = "Entry Point"

    _entity_class = "core.entity.entry_points.EntryPoint"

    _entity_reader_class = None  # TO-DO: define proper entity reader

    _entity_filter_list = {
        "belonging_module": ["core.entity.corefacility_module.CorefacilityModule", None],
        "alias": [str, None]
    }
