from pathlib import Path
from parameterized import parameterized

from core.test.data_providers.file_data_provider import file_data_provider
from roi.entity import RectangularRoi
from ..base_list_test import BaseListTest

TEST_DATA = Path(__file__).parent / "test_list_provider.csv"


class TestRectangularRoiList(BaseListTest):
    """
    Testing retrieving rectangular ROI lists
    """

    entity_class = RectangularRoi
    entity_search_path = "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/rectangular/"

    @classmethod
    def data_provider(cls):
        def kwargs(left, right, top, bottom):
            return {"left": left, "right": right, "top": top, "bottom": bottom}

        return [
            ("test_project", 1, kwargs(0, 2, 1, 3)),
            ("test_project", 2, kwargs(10, 12, 11, 13)),
            ("test_project", 2, kwargs(20, 22, 21, 23)),
            ("test_project", 3, kwargs(30, 32, 31, 33)),
            ("test_project", 3, kwargs(40, 42, 41, 43)),
            ("test_project", 3, kwargs(50, 52, 51, 53)),
            ("test_project1", 1, kwargs(60, 62, 61, 63))
        ]

    @parameterized.expand(file_data_provider(TEST_DATA))
    def test_base_search(self, token_id, project_alias, map_alias, expected_status_code):
        """
        Testing permisssion and validity of rectangular ROIs
        """
        self._test_base_search(token_id, project_alias, map_alias, expected_status_code)
