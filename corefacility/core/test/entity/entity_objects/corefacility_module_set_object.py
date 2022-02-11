from core import App as CoreApp, CorefacilityModule

from core.test.entity_set.entity_set_objects.entity_set_object import EntitySetObject
from core.test.data_providers.module_providers import module_provider


class CorefacilityModuleSetObject(EntitySetObject):
    """
    Defines the entity list
    """

    _entity_class = CorefacilityModule

    def __init__(self, _entity_list=None):
        if _entity_list is not None:
            self._entities = _entity_list
        else:
            self._entities = []
            for module_info in module_provider():
                module = module_info[0]()
                self._entities.append(module)

    def filter_by_is_root_module(self, is_root_module):
        if is_root_module:
            self._entities = list(filter(lambda module: isinstance(module, CoreApp), self._entities))
        else:
            self._entities = list(filter(lambda module: not isinstance(module, CoreApp), self._entities))

    def data_provider(self):
        return None

    def filter_by_entry_point(self, entry_point):
        self._entities = list(filter(lambda module: module.parent_entry_point is entry_point, self._entities))

    def filter_by_is_enabled(self, is_enabled):
        self._entities = list(filter(lambda module: module.is_enabled == is_enabled, self._entities))

    def filter_by_is_application(self, is_application):
        self._entities = list(filter(lambda module: module.is_application == is_application, self._entities))
