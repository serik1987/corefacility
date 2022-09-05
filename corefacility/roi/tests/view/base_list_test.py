import os
from time import time
from pathlib import Path
import numpy
from rest_framework import status

from core.entity.project import ProjectSet
from core.test.views.list_test.base_test_class import BaseTestClass
from imaging.entity import MapSet
from imaging.tests.views.map_list_mixin import MapListMixin


class BaseListTest(MapListMixin, BaseTestClass):
    """
    This is the base class for testing pinwheel lists and rectangular ROI lists
    """

    SAMPLE_FILE = Path(__file__).parent.parent.parent.parent / \
                  "imaging/tests/data_providers/sample_maps/c010_ori00_filt.npz"

    map_uploading_path = "/api/{version}/core/projects/{project}/imaging/data/{map}/npy/"

    map_processing_path = None
    """ Path template for the map processing request """

    entity_class = None
    """ Class of the tested entity (must be a subclass of the core.entity.entity.Entity component) """

    entity_set_class = None
    """ Class of set of the tested entity """

    entity_search_path = None
    """ Please, type the full path to entity list. You can use {project} and {map} placeholders that will 
     be replaced by project and map alias respectively """

    entity_list = None
    """ Dynamic variable filled by dictionary of all tested entities from the testing environment """

    entity_id_list = None
    """ This is also dynamic property that contains list of all entity IDs """

    @classmethod
    def setUpTestData(cls):
        if cls.entity_class is None:
            raise NotImplementedError("Please, implement the 'entity_class' public property")
        super().setUpTestData()
        cls.create_test_environment(add_roi_application=True)
        cls.entity_list = dict()
        cls.entity_id_list = list()
        for project_alias, map_index, kwargs in cls.data_provider():
            map_alias = cls.project_maps[project_alias][map_index].alias
            if project_alias not in cls.entity_list:
                cls.entity_list[project_alias] = dict()
            if map_alias not in cls.entity_list[project_alias]:
                cls.entity_list[project_alias][map_alias] = list()
            entity = cls.entity_class(map=cls.project_maps[project_alias][map_index], **kwargs)
            entity.create()
            cls.entity_list[project_alias][map_alias].append(entity)
            cls.entity_id_list.append(entity.id)

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

    def _test_map_processing(self, token_id, project_alias, map_alias, data_index, upload_map, expected_status_code):
        """
        Tests the ROI processing
        """
        headers = self.get_authorization_headers(token_id)
        if upload_map == "auto":
            map_uploading_path = self.map_uploading_path.format(version=self.API_VERSION, project=project_alias,
                                                                map=map_alias)
            with open(self.SAMPLE_FILE, "rb") as sample_file:
                uploading_result = self.client.patch(map_uploading_path, {"file": sample_file},
                                                     format="multipart", **headers)
            self.assertEquals(uploading_result.status_code, status.HTTP_200_OK,
                              "Unexpected response status during the file upload")
        roi_processing_path = self.map_processing_path.format(
            version=self.API_VERSION, project=project_alias, map=map_alias, roi=self.entity_id_list[data_index])
        request_start_time = time()
        response = self.client.post(roi_processing_path, follow=True, **headers)
        request_finish_time = time()
        self.assertLess(request_finish_time - request_start_time, 1.0,
                        "The request is too busy")
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
        target_map = None
        if expected_status_code < status.HTTP_300_MULTIPLE_CHOICES:
            expected_project = ProjectSet().get(project_alias)
            expected_map = MapSet().get(map_alias)
            self.assert_data_valid(response, expected_map, data_index)
            full_map_path = os.path.join(expected_project.project_dir, response.data['data'])
            self.assertTrue(os.path.isfile(full_map_path), "The processed map has not been saved")
        return target_map

    def assert_data_valid(self, response, expected_map, data_index):
        raise NotImplementedError()
