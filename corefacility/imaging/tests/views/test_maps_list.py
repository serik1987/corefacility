from rest_framework import status
from parameterized import parameterized

from core.entity.project import ProjectSet
from core.test.views.list_test.base_test_class import BaseTestClass
from imaging import App
from imaging.models.enums import MapType
from imaging.entity import Map

from .map_list_mixin import MapListMixin


class TestMapList(MapListMixin, BaseTestClass):

    MAP_LIST_PATH = "/api/{version}/core/projects/{project_alias}/imaging/data/"

    application = App()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment(project_number=2)

    def setUp(self):
        super().setUp()
        self.initialize_projects()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_test_environment()
        super().tearDownClass()

    @parameterized.expand([
        ("ordinary_user", "test_project", status.HTTP_404_NOT_FOUND),
        ("full", "test_project", status.HTTP_200_OK),
        ("data_add", "test_project1", status.HTTP_200_OK),
        ("data_view", "test_project", status.HTTP_200_OK),
        ("superuser", "test_project1", status.HTTP_200_OK),
        ("no_access", "test_project", status.HTTP_404_NOT_FOUND),
        ("data_process", "test_project1", status.HTTP_200_OK),
        ("data_process", "test_project", status.HTTP_200_OK),
        ("data_full", "test_project", status.HTTP_200_OK),
        ("data_full", "test_project1", status.HTTP_200_OK),
        ("full", "test_project1", status.HTTP_200_OK),
        ("data_view", "test_project1", status.HTTP_200_OK),
        ("no_access", "test_project1", status.HTTP_404_NOT_FOUND),
        ("data_add", "test_project", status.HTTP_200_OK),
        ("ordinary_user", "test_project1", status.HTTP_404_NOT_FOUND),
        ("superuser", "test_project", status.HTTP_200_OK),
    ])
    def test_map_list(self, token_id, project_alias, expected_status_code):
        """
        Provides the map list test
        :param token_id: login of the user that is trying to get access to the map list
        :param project_alias: alias of the project this map list relates to
        :param expected_status_code: status code to be expected
        :return:
        """
        path = self.MAP_LIST_PATH.format(version=self.API_VERSION, project_alias=project_alias)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        if expected_status_code >= status.HTTP_300_MULTIPLE_CHOICES:
            return
        self.assertEquals(response.data['count'], len(response.data['results']),
                          "Unexpected value of the response 'count' field")
        self.assertEquals(response.data['count'], len(self.project_maps[project_alias]),
                          "Unexpected number of maps in the results")
        for map_index in range(response.data['count']):
            self.assert_map(response.data['results'][map_index], self.project_maps[project_alias][map_index])

    def assert_map(self, actual_map, expected_map):
        """
        Asserts that two maps are equal
        :param actual_map: the map information revealed by the map search request
        :param expected_map: the map that has been actually stored in the database
        :return: nothing
        """
        self.assertEquals(actual_map['id'], expected_map.id, "Unexpected map ID")
        self.assertEquals(actual_map['alias'], expected_map.alias, "Unexpected map alias")
        self.assertEquals(actual_map['type'], str(expected_map.type), "Unexpected map type")


del BaseTestClass
