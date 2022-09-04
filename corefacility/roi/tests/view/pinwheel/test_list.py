from rest_framework import status
from parameterized import parameterized

from core.test.views.list_test.base_test_class import BaseTestClass
from imaging.tests.views.map_list_mixin import MapListMixin
from roi.entity import Pinwheel


def base_search_provider():
    return [
        ("superuser", "test_project", "c022_X210", status.HTTP_200_OK),
        ("superuser", "test_project", "c022_X100", status.HTTP_200_OK),
        ("superuser", "test_project", "c023_X2", status.HTTP_200_OK),
        ("superuser", "test_project", "c023_X300", status.HTTP_404_NOT_FOUND),
        ("superuser", "test_test", "c025_X300", status.HTTP_404_NOT_FOUND),
        ("superuser", "test_project", "c025_X300", status.HTTP_200_OK),
        ("superuser", "test_project1", "c040_X100", status.HTTP_200_OK),
        ("superuser", "test_project1", "c040_X101", status.HTTP_200_OK),
        ("no_access", "test_project1", "c040_X101", status.HTTP_404_NOT_FOUND),
        ("superuser", "test_project", "c040_X101", status.HTTP_404_NOT_FOUND),
        (None, "test_project", "c022_X210", status.HTTP_401_UNAUTHORIZED),
    ]


class TestPinwheelList(MapListMixin, BaseTestClass):

    PINWHEEL_SEARCH_PATH = "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/pinwheels/"

    entity_list = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment(add_roi_application=True)
        cls.entity_list = dict()
        for project_alias, map_index, kwargs in cls.pinwheel_provider():
            map_alias = cls.project_maps[project_alias][map_index].alias
            if project_alias not in cls.entity_list:
                cls.entity_list[project_alias] = dict()
            if map_alias not in cls.entity_list[project_alias]:
                cls.entity_list[project_alias][map_alias] = list()
            entity = Pinwheel(map=cls.project_maps[project_alias][map_index], **kwargs)
            entity.create()
            cls.entity_list[project_alias][map_alias].append(entity)

    @classmethod
    def pinwheel_provider(cls):
        def kwargs(x, y):
            return {"x": x, "y": y}

        return [
            ("test_project", 1, kwargs(0, 2)),
            ("test_project", 2, kwargs(10, 12)),
            ("test_project", 2, kwargs(20, 22)),
            ("test_project", 3, kwargs(30, 32)),
            ("test_project", 3, kwargs(40, 42)),
            ("test_project", 3, kwargs(50, 52)),
            ("test_project1", 1, kwargs(60, 62))
        ]

    def setUp(self):
        super().setUp()
        self.initialize_projects()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_test_environment()
        super().tearDownClass()

    @parameterized.expand(base_search_provider())
    def test_base_search(self, token_id, project_alias, map_alias, expected_status_code):
        """
        Tests the base searching facility
        """
        pinwheel_search_path = self.PINWHEEL_SEARCH_PATH.format(
            version=self.API_VERSION, project=project_alias, map=map_alias)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(pinwheel_search_path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        if expected_status_code < status.HTTP_300_MULTIPLE_CHOICES:
            actual_data = response.data['results']
            if map_alias not in self.entity_list[project_alias]:
                self.assertEquals(len(actual_data), 0, "The pinwheel list must be empty")
            else:
                expected_data = self.entity_list[project_alias][map_alias]
                self.assertEquals(len(actual_data), len(expected_data), "Unexpected number of pinwheels in the list")
                for index in range(len(actual_data)):
                    actual_pinwheel = actual_data[index]
                    expected_pinwheel = expected_data[index]
                    self.assertEquals(actual_pinwheel['id'], expected_pinwheel.id, "Unexpected pinwheel ID")
                    self.assertEquals(actual_pinwheel['x'], expected_pinwheel.x, "Unexpected pinwheel X")
                    self.assertEquals(actual_pinwheel['y'], expected_pinwheel.y, "Unexpected pinwheel Y")
