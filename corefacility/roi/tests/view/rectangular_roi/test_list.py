from pathlib import Path
from time import time
from rest_framework import status
from parameterized import parameterized

from core.test.data_providers.file_data_provider import file_data_provider
from roi.entity import RectangularRoi
from ..base_list_test import BaseListTest

TEST_DATA = Path(__file__).parent / "test_list_provider.csv"
SAMPLE_FILE = Path(__file__).parent.parent.parent.parent.parent / \
              "imaging/tests/data_providers/sample_maps/c010_ori00_filt.npz"


class TestRectangularRoiList(BaseListTest):
    """
    Testing retrieving rectangular ROI lists
    """

    entity_class = RectangularRoi
    map_uploading_path = "/api/{version}/core/projects/{project}/imaging/data/{map}/npy/"
    entity_search_path = "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/rectangular/"
    roi_processing_path =\
        "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/rectangular/{roi}/cut_map/"

    @classmethod
    def data_provider(cls):
        def kwargs(left, right, top, bottom):
            return {"left": left, "right": right, "top": top, "bottom": bottom}

        return [
            ("test_project", 1, kwargs(0, 2, 1, 8)),
            ("test_project", 2, kwargs(10, 12, 11, 18)),
            ("test_project", 2, kwargs(20, 22, 21, 28)),
            ("test_project", 3, kwargs(30, 32, 31, 38)),
            ("test_project", 3, kwargs(40, 42, 41, 48)),
            ("test_project", 3, kwargs(50, 52, 51, 58)),
            ("test_project1", 1, kwargs(60, 62, 61, 68))
        ]

    @parameterized.expand(file_data_provider(TEST_DATA))
    def test_base_search(self, token_id, project_alias, map_alias, expected_status_code):
        """
        Tests permission and validity of rectangular ROIs
        """
        self._test_base_search(token_id, project_alias, map_alias, expected_status_code)

    def test_roi_processing(self, token_id="superuser", project_alias="test_project", map_alias="c022_X100",
                            roi_index=0, upload_map="auto"):
        headers = self.get_authorization_headers(token_id)
        if upload_map == "auto":
            map_uploading_path = self.map_uploading_path.format(version=self.API_VERSION, project=project_alias,
                                                                map=map_alias)
            with open(SAMPLE_FILE, "rb") as sample_file:
                uploading_result = self.client.patch(map_uploading_path, {"file": sample_file},
                                                     format="multipart", **headers)
            self.assertEquals(uploading_result.status_code, status.HTTP_200_OK)
        roi_processing_path = self.roi_processing_path.format(
            version=self.API_VERSION, project=project_alias, map=map_alias, roi=self.entity_id_list[roi_index])
        request_start_time = time()
        response = self.client.post(roi_processing_path, follow=True, **headers)
        request_finish_time = time()
        self.assertLess(request_finish_time - request_start_time, 1.0,
                        "The request is too busy")
        print(response, response.data)
