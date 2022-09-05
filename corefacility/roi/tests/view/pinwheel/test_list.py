from rest_framework import status
from parameterized import parameterized

from roi.entity import Pinwheel, PinwheelSet
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
    entity_set_class = PinwheelSet
    entity_search_path = "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/pinwheels/"

    map_processing_path =\
        "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/pinwheels/distance_map/"

    @classmethod
    def data_provider(cls):
        def kwargs(x, y):
            return {"x": x, "y": y}

        return [
            ("test_project", 1, kwargs(0, 2)),
            ("test_project", 2, kwargs(100, 120)),
            ("test_project", 2, kwargs(200, 220)),
            ("test_project", 3, kwargs(300, 320)),
            ("test_project", 3, kwargs(400, 420)),
            ("test_project", 3, kwargs(500, 500)),
            ("test_project1", 1, kwargs(5000, 10000))
        ]

    def setUp(self):
        super().setUp()
        self.initialize_projects()

    @classmethod
    def tearDownClass(cls):
        # cls.destroy_test_environment()
        super().tearDownClass()

    @parameterized.expand(base_search_provider())
    def test_base_search(self, token_id, project_alias, map_alias, expected_status_code):
        """
        Tests the base searching facility
        """
        self._test_base_search(token_id, project_alias, map_alias, expected_status_code)

    @parameterized.expand([
        ("data_add", "test_project", "c022_X210", 0, "auto", status.HTTP_400_BAD_REQUEST),
        ("data_add", "test_project", "c022_X100", 0, "auto", status.HTTP_200_OK),
        ("data_add", "test_project", "c023_X2", 0, "auto", status.HTTP_200_OK),
        ("data_add", "test_project", "c025_X300", 0, "auto", status.HTTP_200_OK),
        ("data_add", "test_project1", "c040_X100", 0, "auto", status.HTTP_400_BAD_REQUEST),
        ("data_add", "test_project1", "c040_X101", 0, "auto", status.HTTP_200_OK),
    ])
    def test_distance_map(self, token_id, project_alias, map_alias, roi_index, upload_map, expected_status_code):
        """
        Tests for the distance map feature
        """
        self._test_map_processing(token_id, project_alias, map_alias, roi_index, upload_map, expected_status_code)

    def assert_data_valid(self, response, expected_map, data_index):
        pass


del BaseListTest
