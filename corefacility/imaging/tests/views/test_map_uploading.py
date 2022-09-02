import os
from pathlib import Path

import numpy as np
from rest_framework import status
from parameterized import parameterized

from core.test.views.project_data_test_mixin_small import ProjectDataTestMixinSmall
from core.test.views.avatar_test.file_upload_test import FileUploadTest
from imaging import App
from imaging.entity import Map


class TestMapUploading(ProjectDataTestMixinSmall, FileUploadTest):
    """
    Tests whether the map can be successfully uploaded or deleted
    """

    application = App()
    """ Tested application """

    functional_map = None
    """ A functional map being under the test """

    sample_file = str(Path(__file__).parent.parent / "data_providers/sample_maps/c010_dir00_filt.npz")
    """ The file that shall be uploaded during the base uploading tests """

    sample_file_2 = str(Path(__file__).parent.parent / "data_providers/sample_maps/c010_ori00_filt.npz")

    upload_request_method = "PATCH"
    """ Defines the request method responsible for the file upload """

    upload_request_path = "/api/{version}/core/projects/{project_alias}/imaging/data/{data_name}/npy/"
    """ Template for the uploading path """

    update_request_path = "/api/{version}/core/projects/{project_alias}/imaging/data/{data_name}/"

    upload_response_status_code = status.HTTP_200_OK
    """ Expected status code for the updated response """

    delete_request_method = "DELETE"
    """ Defines the request method responsible for the file delete """

    delete_response_status_code = status.HTTP_200_OK
    """ Expected status code for the delete response """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment()
        cls.functional_map = Map(alias="c023_X210", type="ori", project=cls.project, width=12400, height=12400)
        cls.functional_map.create()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_test_environment()
        super().tearDownClass()

    @parameterized.expand([
        ("superuser", status.HTTP_200_OK, status.HTTP_200_OK),
        ("full", status.HTTP_200_OK, status.HTTP_200_OK),
        ("data_full", status.HTTP_200_OK, status.HTTP_200_OK),
        ("data_add", status.HTTP_200_OK, status.HTTP_403_FORBIDDEN),
        ("data_process", status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN),
        ("data_view", status.HTTP_403_FORBIDDEN, status.HTTP_403_FORBIDDEN),
        ("no_access", status.HTTP_404_NOT_FOUND, status.HTTP_404_NOT_FOUND),
        ("ordinary_user", status.HTTP_404_NOT_FOUND, status.HTTP_404_NOT_FOUND),
    ])
    def test_security(self, token_id, expected_status_code, delete_status_code):
        """
        Provides security test for file uploading
        """
        super()._test_security(token_id, expected_status_code, delete_status_code)

    def test_upload_invalid_file(self):
        invalid_filename = Path(__file__).parent.parent.parent.parent / \
                       "core/test/data_providers/pdf/bind-9.13.3-manual.pdf"
        with open(invalid_filename, "rb") as invalid_file:
            response = self.client.patch(self.get_request_path(), {"file": invalid_file}, format="multipart",
                                         **self.get_authorization_headers("superuser"))
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, "Bad uploaded file")

    def get_request_path(self):
        return self.upload_request_path.format(version=self.API_VERSION, project_alias=self.project.alias,
                                               data_name=self.functional_map.alias)

    def assert_file_exists(self, all_files):
        """
        Checks whether media root contains exactly files mentioned in the list.
        The function will compare file names
        :param all_files: list of all files to be contained.
        :return: nothing
        """
        self.assertEquals(len(os.listdir(self.project.project_dir)), len(all_files),
                          "Unexpected number of files within the project directory")

    def assert_database(self, response):
        """
        Asserts that the file has been presented in the database
        :param response: the response received
        :return: full path to the file
        """
        filename = response.data['data']
        self.assertIsNotNone(filename, "The name of the uploaded file has not been saved to the database")
        full_name = os.path.join(self.project.project_dir, filename)
        self.assertTrue(os.path.exists(full_name), "The uploaded file has not been saved into the project directory")
        data_matrix = np.load(full_name)
        self.assertEquals(data_matrix.shape, (response.data['resolution_y'], response.data['resolution_x']),
                          "The map resolution was not filled")

    def assert_not_in_database(self, response):
        """
        Asserts that the file has not been presented in the database
        :param response: the response received by the file delete request
        :return: nothing
        """
        self.assertIsNone(response.data['data'],
                          "The file has not been successfully removed from the database after its delete")

    def get_update_path(self, response):
        """
        Returns path of the GET response the updates the file uploading information
        :param response: the response which body shall be updated
        :return: path of the updating response
        """
        return self.update_request_path.format(version=self.API_VERSION, project_alias=self.project.alias,
                                               data_name=self.functional_map.alias)

    def get_delete_path(self, updated_response):
        """
        Returns path of the DELETE response
        :param updated_response: the response on file updating request
        :return: path of the updating response
        """
        return self.get_request_path()

    def get_special_delete_path(self):
        """
        Returns the request path specially for the sole delete (aka test_delete) test
        :return: the request path
        """
        return self.get_request_path()


del FileUploadTest
