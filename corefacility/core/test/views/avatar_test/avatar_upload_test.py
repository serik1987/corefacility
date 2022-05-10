import os

from django.conf import settings
from rest_framework import status

from .image_upload_test import ImageUploadTest


class AvatarUploadTest(ImageUploadTest):
    """
    A base class for avatar uploading and deleting
    """

    upload_request_method = "PATCH"
    upload_response_status_code = status.HTTP_200_OK
    delete_request_method = "DELETE"
    delete_response_status_code = status.HTTP_200_OK
    desired_image_size = (150, 150)

    resource_name = None
    """ Name of the resource (a URI segment) to which the avatar shall be uploaded """

    entity_set_class = None
    """ Class of the entity set to which the avatar shall be attached """

    entity_avatar_field = "avatar"
    """ Name of the avatar field """

    def assert_file_exists(self, all_files):
        """
        Checks whether media root contains exactly files mentioned in the list.
        The function will compare file names.

        :param all_files: list of all files to be contained.
        :return: nothing
        """
        actual_files = []
        for original_file in os.listdir(settings.MEDIA_ROOT):
            original_full_file = os.path.join(settings.MEDIA_ROOT, original_file)
            if os.path.isfile(original_full_file):
                actual_files.append(original_full_file)
        self.assertEquals(len(actual_files), len(all_files))

    def assert_database(self, response):
        """
        Asserts that the file has been presented in the database

        :param response: the response received
        :return: full file name
        """
        avatar_url = self.get_uploaded_file_url(response)
        self.assertTrue(avatar_url.startswith(settings.MEDIA_URL), "The file doesn't seem to be uploaded")
        filename = avatar_url.split(settings.MEDIA_URL)[1]
        fullname = os.path.join(settings.MEDIA_ROOT, filename)
        self.assertTrue(os.path.isfile(fullname), "The uploaded file doesn't seem to be saved")
        return fullname

    def assert_not_in_database(self, response):
        """
        Asserts that the file has not been presented in the database

        :param response: the response received by the file delete request
        :return: nothing
        """
        avatar_url = self.get_uploaded_file_url(response)
        self.assertTrue(avatar_url.startswith(settings.STATIC_URL), "The file doesn't seem to be deleted")

    def get_request_path(self):
        """
        Returns the request path for the uploading request

        :return: a string containing the request path
        """
        return "/api/{version}/{resource_name}/{resource_id}/avatar/".format(
            version=self.API_VERSION,
            resource_name=self.get_resource_name(),
            resource_id=self.get_random_resource_id(),
        )

    def get_uploaded_file_url(self, response):
        """
        Extracts the file URL from the response

        :param response: the response from which the file URL shall be extracted
        :return: nothing
        """
        entity_id = response.data['id']
        entity_set = self.get_entity_set_class()()
        entity = entity_set.get(entity_id)
        avatar_url = getattr(entity, self.entity_avatar_field).url
        return avatar_url

    def get_update_path(self, response):
        """
        Returns path of the GET response the updates the file uploading information

        :param response: the response which body shall be updated
        :return: path of the updating response
        """
        entity_id = response.data['id']
        return self.get_entity_detail_path(entity_id)

    def get_special_delete_path(self):
        """
        Returns the request path specially for the sole delete (aka test_delete) test.

        :return: the request path
        """
        return self.get_request_path()

    def get_delete_path(self, updated_response):
        """
        Returns path of the DELETE response

        :param updated_response: the response on file updating request
        :return: path of the updating response
        """
        entity_id = updated_response.data['id']
        return "/api/{version}/{resource_name}/{resource_id}/avatar/".format(
            version=self.API_VERSION,
            resource_name=self.get_resource_name(),
            resource_id=entity_id
        )

    def get_resource_name(self):
        if self.resource_name is None:
            raise NotImplementedError("Please, define the resource name")
        return self.resource_name

    def get_random_resource_id(self):
        """
        Returns a random resource ID

        :return: a random resource ID
        """
        raise NotImplementedError("Please, define the get_random_resource_id method")

    def get_entity_set_class(self):
        if self.entity_set_class is None:
            raise NotImplementedError("entity_set_class public property")
        return self.entity_set_class


del ImageUploadTest
