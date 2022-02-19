from core.entity.entity_exceptions import EntityOperationNotPermitted
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

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if isinstance(lookup, str) and \
                not ("parent_module" in self._entity_filters or "parent_module_is_root" in self._entity_filters):
            raise EntityOperationNotPermitted()
        return super().get(lookup)
