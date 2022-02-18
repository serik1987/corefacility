from core import App as CoreApp
from core.entity.entry_points.entry_point import EntryPoint

from core.test.entity_set.entity_set_objects.entity_set_object import EntitySetObject
from core.test.data_providers.module_providers import entry_point_provider


class EntryPointSetObject(EntitySetObject):
    """
    This is a testing instance that will be used for testing entry point sets
    """

    _entity_class = EntryPoint

    def __init__(self, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param _entity_list: This is an internal argument. Don't use it.
        """
        if _entity_list is not None:
            self._entities = _entity_list
        else:
            self._entities = []
            for entry_point_info in entry_point_provider():
                entry_point_class = entry_point_info['entry_point']
                entry_point = entry_point_class()
                self._entities.append(entry_point)

    def sort(self):
        """
        Sorts all entry points in alphabetical order

        :return: nothing
        """
        self._entities = sorted(self._entities, key=lambda entry_point: entry_point.name)

    def filter_by_parent_module_is_root(self, is_parent_root):
        """
        Filters entry points by whether they belong to the core module or not.

        :param is_parent_root: True is all entry points must belong to the core module, False if all of them must
        not belong to the core module
        :return: nothing
        """
        if is_parent_root:
            def filter_operator(entry_point):
                return isinstance(entry_point.belonging_module, CoreApp)
        else:
            def filter_operator(entry_point):
                return not isinstance(entry_point.belonging_module, CoreApp)
        self._entities = list(filter(filter_operator, self._entities))

    def filter_by_parent_module(self, parent_module):
        """
        Filters by parent module
        
        :param parent_module: the parent module by which the data must be filtered
        :return: nothing
        """
        self._entities = list(filter(lambda entry_point: entry_point.belonging_module.uuid == parent_module.uuid,
                                     self._entities))
