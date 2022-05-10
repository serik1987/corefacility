from rest_framework import status

from ..base_view_test import BaseViewTest
from ...media_files_mixin import MediaFilesMixin


class FileUploadTest(MediaFilesMixin, BaseViewTest):
    """
    This is the base class for all file upload and delete tests
    """

    sample_file = None
    """ The file that shall be uploaded during the base uploading tests """

    sample_file_2 = None
    """ A sample file for upload_upload tests """

    upload_request_method = None
    """ Defines the request method responsible for the file upload """

    delete_request_method = None
    """ Defines the request method responsible for the file delete """

    upload_response_status_code = None
    """ Expected status code for the updated response """

    delete_response_status_code = None
    """ Expected status code for the delete response """

    superuser_required = True
    ordinary_user_required = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_media_root_backup()

    def tearDown(self):
        self.clear_media_root()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.restore_media_root_backup()
        super().tearDownClass()

    def test_file_upload(self):
        """
        Provides a base check for the file upload

        :return: nothing
        """
        sample_file = self.get_sample_file()
        response = self.upload(sample_file)
        self.assert_file_exists([sample_file])
        old_file = self.assert_database(response)
        new_response = self.update(response)
        new_file = self.assert_database(new_response)
        self.assertEquals(old_file, new_file, "The uploaded file URL can't be retrieved")

    def test_file_upload_and_delete(self):
        """
        Provides file uploading and deleting

        :return: nothing
        """
        sample_file = self.get_sample_file()
        uploaded_response = self.upload(sample_file)
        deleted_response = self.delete(uploaded_response)
        self.assert_file_exists([])
        self.assert_not_in_database(deleted_response)
        updated_response = self.update(uploaded_response)
        self.assert_not_in_database(updated_response)

    def test_file_upload_and_upload(self):
        """
        Tests file uploading and uploading again

        :return: nothing
        """
        sample_file_1 = self.get_sample_file()
        self.upload(sample_file_1)
        sample_file_2 = self.get_sample_file_2()
        uploaded_response_2 = self.upload(sample_file_2)
        self.assert_file_exists([sample_file_2])
        self.assert_database(uploaded_response_2)
        updated_response = self.update(uploaded_response_2)
        self.assert_database(updated_response)

    def test_file_delete(self):
        """
        Tests file delete

        :return: nothing
        """
        delete_function = self.get_delete_request_function()
        request_path = self.get_special_delete_path()
        auth_headers = self.get_authorization_headers("superuser")
        response = delete_function(request_path, **auth_headers)
        self.assertEquals(response.status_code, self.get_delete_response_status_code(),
                          "Unexpected file delete status code")
        self.assert_file_exists([])
        self.assert_not_in_database(response)

    def _test_security(self, token_id, expected_status_code):
        """
        Provides a security test

        :param token_id: ID of the authorization token or None for unauthorized responses
        :param expected_status_code: status code to expect
        :return: nothing
        """
        upload_file = self.get_sample_file()
        headers = self.get_authorization_headers(token_id)
        upload_response = self.upload(upload_file, expected_status_code, token_id)
        self.assertEquals(upload_response.status_code, expected_status_code,
                          "Unexpected upload status code")
        delete_function = self.get_delete_request_function()
        delete_path = self.get_special_delete_path()
        delete_response = delete_function(delete_path, **headers)
        self.assertEquals(delete_response.status_code, expected_status_code, "Unexpected delete status code")

    def _test_valid_upload_type(self, filename, expected_status_code):
        response = self.upload(filename, expected_status_code)
        self.assert_correct_processing(response, filename)

    def upload(self, filename, expected_status_code=None, token_id="superuser"):
        """
        Uploads the file to the server

        :param filename: full path to the uploading file. The file shall be located in the client
        :param expected_status_code: a status code that you are expected to receive or None if such a code shall be
            defined by the 'upload_response_status_code' property
        :param token_id: ID of the authorization token
        :return: the REST response after the uploading facility
        """
        upload_function = self.get_upload_request_function()
        request_path = self.get_request_path()
        auth_headers = self.get_authorization_headers(token_id)
        if expected_status_code is None:
            expected_status_code = self.get_upload_response_status_code()
        with open(filename, "rb") as file_handle:
            response = upload_function(request_path,
                                       data={"file": file_handle},
                                       format="multipart",
                                       **auth_headers)
        self.assertEquals(response.status_code, expected_status_code,
                          "The file uploading response has unexpected status code")
        return response

    def update(self, response):
        """
        Updates the file upload information containing in the response

        :param response: the response which body shall be updated
        :return: the response with the updated body
        """
        path = self.get_update_path(response)
        auth = self.get_authorization_headers("superuser")
        response = self.client.get(path, **auth)
        self.assertEquals(response.status_code, status.HTTP_200_OK, "The file uploading info can't be reloaded")
        return response

    def delete(self, uploaded_response):
        """
        Deletes the file

        :param uploaded_response: the response received after file upload
        :return: the response received after file delete
        """
        path = self.get_delete_path(uploaded_response)
        function = self.get_delete_request_function()
        auth = self.get_authorization_headers("superuser")
        delete_response = function(path, **auth)
        self.assertEquals(delete_response.status_code, self.get_delete_response_status_code(),
                          "Unexpected status code for the DELETE response")
        return delete_response

    def assert_file_exists(self, all_files):
        """
        Checks whether media root contains exactly files mentioned in the list.
        The function will compare file names.

        :param all_files: list of all files to be contained.
        :return: nothing
        """
        raise NotImplementedError("assert_file_exists")

    def assert_database(self, response):
        """
        Asserts that the file has been presented in the database

        :param response: the response received
        :return: full path to the file
        """
        raise NotImplementedError("assert_database")

    def assert_not_in_database(self, response):
        """
        Asserts that the file has not been presented in the database

        :param response: the response received by the file delete request
        :return: nothing
        """
        raise NotImplementedError("assert_not_in_database")

    def assert_correct_processing(self, response, filename):
        """
        Asserts that the response has been processed by one of the following way.
        Either: - response code is 2xx
                - the file has been saved to the hard disk drive
                - the file has been attached to the entity
        Or: - response code is not 2xx
            - the file has not been saved to the hard disk drive

        :param response: the response received by the upload request
        :param filename: name of the file (on the client storage!) that has been uploaded
        :return: nothing
        """
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            self.assert_file_exists([filename])
            self.assert_database(response)
        else:
            self.assert_file_exists([])

    def get_uploaded_file_url(self, response):
        """
        Extracts the file URL from the response

        :param response: the response from which the file URL shall be extracted
        :return: nothing
        """
        raise NotImplementedError("get_uploaded_file_url")

    def get_sample_file(self):
        if self.sample_file is None:
            raise NotImplementedError("Please, define the 'sample_file' public property")
        return self.sample_file

    def get_sample_file_2(self):
        if self.sample_file_2 is None:
            raise NotImplementedError("Please, define the 'sample_file_2' public property")
        return self.sample_file_2

    def get_upload_request_function(self):
        """
        Returns a function for a file uploading

        :return: an APIClient's method that will be used for the request upload
        """
        if self.upload_request_method is None:
            raise NotImplementedError("Please, define the 'upload_request_method property")
        return getattr(self.client, self.upload_request_method.lower())

    def get_delete_request_function(self):
        """
        Returns a function for a file deleting

        :return: an APIClient's method that will be used for the request delete
        """
        if self.delete_request_method is None:
            raise NotImplementedError("Please, define the 'delete_request_method' property")
        return getattr(self.client, self.delete_request_method.lower())

    def get_request_path(self):
        """
        Returns the request path for the uploading request

        :return: a string containing the request path
        """
        raise NotImplementedError("Please, define the get_request_path")

    def get_special_delete_path(self):
        """
        Returns the request path specially for the sole delete (aka test_delete) test.

        :return: the request path
        """
        raise NotImplementedError("Please, define the get_special_delete_path")

    def get_update_path(self, response):
        """
        Returns path of the GET response the updates the file uploading information

        :param response: the response which body shall be updated
        :return: path of the updating response
        """
        raise NotImplementedError("get_update_path")

    def get_delete_path(self, uploaded_response):
        """
        Returns path of the DELETE response that deletes the previously updated file

        :param uploaded_response: the response that has been uploaded a file
        :return: path of the deleted response
        """
        raise NotImplementedError("get_delete_path")

    def get_upload_response_status_code(self):
        if self.upload_response_status_code is None:
            raise NotImplementedError("'upload_response_status_code' public property")
        return self.upload_response_status_code

    def get_delete_response_status_code(self):
        if self.delete_response_status_code is None:
            raise NotImplementedError("'delete_response_status_code' public property")
        return self.delete_response_status_code


del BaseViewTest
