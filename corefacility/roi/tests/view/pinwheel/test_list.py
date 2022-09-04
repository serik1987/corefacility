from rest_framework import status
from parameterized import parameterized

from roi.entity import Pinwheel
from ..base_list_test import BaseListTest


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


class TestPinwheelList(BaseListTest):

    entity_class = Pinwheel
    entity_search_path = "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/pinwheels/"

    @classmethod
    def data_provider(cls):
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
        self._test_base_search(token_id, project_alias, map_alias, expected_status_code)


del BaseListTest
