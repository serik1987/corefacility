from rest_framework import status

from core.test.views.list_test.base_test_class import BaseTestClass
from imaging.tests.views.map_list_mixin import MapListMixin


class BaseListTest(MapListMixin, BaseTestClass):
    """
    This is the base class for testing pinwheel lists and rectangular ROI lists
    """

    entity_class = None
    """ Class of the tested entity (must be a subclass of the core.entity.entity.Entity component) """

    entity_search_path = None
    """ Please, type the full path to entity list. You can use {project} and {map} placeholders that will 
     be replaced by project and map alias respectively """

    entity_list = None
    """ Dynamic variable filled by dictionary of all tested entities from the testing environment """

    @classmethod
    def setUpTestData(cls):
        if cls.entity_class is None:
            raise NotImplementedError("Please, implement the 'entity_class' public property")
        super().setUpTestData()
        cls.create_test_environment(add_roi_application=True)
        cls.entity_list = dict()
        for project_alias, map_index, kwargs in cls.data_provider():
            map_alias = cls.project_maps[project_alias][map_index].alias
            if project_alias not in cls.entity_list:
                cls.entity_list[project_alias] = dict()
            if map_alias not in cls.entity_list[project_alias]:
                cls.entity_list[project_alias][map_alias] = list()
            entity = cls.entity_class(map=cls.project_maps[project_alias][map_index], **kwargs)
            entity.create()
            cls.entity_list[project_alias][map_alias].append(entity)

    @classmethod
    def data_provider(cls):
        """
        Returns list of tuples (project_alias, map_alias, dictionary_of_entity_arguments)
        Such tuples are need to finish creating the test environment
        """
        raise NotImplementedError("data_provider")

    def _test_base_search(self, token_id, project_alias, map_alias, expected_status_code):
        """
        Tests the base searching facility
        """
        if self.entity_search_path is None:
            raise NotImplementedError("Please, implement the entity search path")
        expected_status_code = int(expected_status_code)
        entity_search_path = self.entity_search_path.format(
            version=self.API_VERSION, project=project_alias, map=map_alias)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(entity_search_path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        if expected_status_code < status.HTTP_300_MULTIPLE_CHOICES:
            actual_data = response.data['results']
            if map_alias not in self.entity_list[project_alias]:
                self.assertEquals(len(actual_data), 0, "The pinwheel list must be empty")
            else:
                expected_data = self.entity_list[project_alias][map_alias]
                self.assertEquals(len(actual_data), len(expected_data), "Unexpected number of entities in the list")
                for index in range(len(actual_data)):
                    actual_entity = actual_data[index]
                    expected_entity = expected_data[index]
                    for field, value in actual_entity.items():
                        actual_value = actual_entity[field]
                        expected_value = getattr(expected_entity, field)
                        self.assertEquals(actual_value, expected_value, "Unexpected " + field)
