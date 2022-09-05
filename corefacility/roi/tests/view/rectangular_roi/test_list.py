import os
from pathlib import Path
from time import time
import numpy
from rest_framework import status
from parameterized import parameterized

from core.entity.project import ProjectSet
from core.test.data_providers.file_data_provider import file_data_provider
from imaging.entity import MapSet
from roi.entity import RectangularRoi, RectangularRoiSet
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
            ("test_project", 1, kwargs(1000, 2000, 1200, 1800)),
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

    @parameterized.expand([
        ("data_add", "test_project", "c022_X100", 0, "auto", status.HTTP_400_BAD_REQUEST),
        ("data_add", "test_project", "c022_X100", 0, "none", status.HTTP_400_BAD_REQUEST),
        ("data_add", "test_project", "c023_X2", 1, "auto", status.HTTP_200_OK),
        ("data_add", "test_project", "c023_X2", 1, "none", status.HTTP_400_BAD_REQUEST),
        ("data_process", "test_project", "c023_X2", 1, "none", status.HTTP_400_BAD_REQUEST),
        ("data_view", "test_project", "c023_X2", 1, "none", status.HTTP_403_FORBIDDEN),
        ("no_access", "test_project", "c023_X2", 1, "none", status.HTTP_404_NOT_FOUND),
    ])
    def test_roi_processing(self, token_id, project_alias, map_alias, roi_index, upload_map, expected_status_code):
        """
        Tests the ROI processing
        """
        headers = self.get_authorization_headers(token_id)
        if upload_map == "auto":
            map_uploading_path = self.map_uploading_path.format(version=self.API_VERSION, project=project_alias,
                                                                map=map_alias)
            with open(SAMPLE_FILE, "rb") as sample_file:
                uploading_result = self.client.patch(map_uploading_path, {"file": sample_file},
                                                     format="multipart", **headers)
            self.assertEquals(uploading_result.status_code, status.HTTP_200_OK,
                              "Unexpected response status during the file upload")
        roi_processing_path = self.roi_processing_path.format(
            version=self.API_VERSION, project=project_alias, map=map_alias, roi=self.entity_id_list[roi_index])
        request_start_time = time()
        response = self.client.post(roi_processing_path, follow=True, **headers)
        request_finish_time = time()
        self.assertLess(request_finish_time - request_start_time, 1.0,
                        "The request is too busy")
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        if expected_status_code < status.HTTP_300_MULTIPLE_CHOICES:
            expected_project = ProjectSet().get(project_alias)
            expected_map = MapSet().get(map_alias)
            expected_roi = RectangularRoiSet().get(self.entity_id_list[roi_index])
            roi_width = expected_roi.right - expected_roi.left
            roi_height = expected_roi.bottom - expected_roi.top
            roi_width_um = roi_width * expected_map.width / expected_map.resolution_x
            roi_height_um = roi_height * expected_map.height / expected_map.resolution_y
            self.assertEquals(response.data['alias'], expected_map.alias + "_cut", "Unexpected map alias")
            self.assertEquals(response.data['resolution_x'], roi_width, "Unexpected map width")
            self.assertEquals(response.data['resolution_y'], roi_height, "Unexpected map height")
            self.assertAlmostEqual(response.data['width'], roi_width_um, delta=1e-8, msg="Unexpected map width")
            self.assertAlmostEqual(response.data['height'], roi_height_um, delta=1e-8, msg="Unexpected map height")
            full_map_path = os.path.join(expected_project.project_dir, response.data['data'])
            self.assertTrue(os.path.isfile(full_map_path), "The processed map has not been saved")
            target_map = numpy.load(full_map_path)
            self.assertEquals(target_map.shape, (roi_height, roi_width), "Target map resolution is bad")
