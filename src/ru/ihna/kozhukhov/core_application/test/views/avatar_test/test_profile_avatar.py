from parameterized import parameterized
from rest_framework import status

from ....entity.entity_sets.user_set import UserSet

from .avatar_upload_test import AvatarUploadTest


class TestProfileAvatar(AvatarUploadTest):
    """
    Tests the profile avatar
    """

    entity_set_class = UserSet

    @parameterized.expand([
        (None, status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", status.HTTP_200_OK),
        ("superuser", status.HTTP_200_OK),
    ])
    def test_security(self, token_id, expected_status_code):
        self._test_security(token_id, expected_status_code)

    @parameterized.expand([
        ("ordinary_user", "user"),
        ("superuser", "superuser"),
    ])
    def test_account_hit(self, token_id, login):
        filename = self.get_sample_file()
        uploaded_response = self.upload(filename, status.HTTP_200_OK, token_id)
        desired_file = self.assert_database(uploaded_response)
        user_retrieve_path = "/api/{version}/users/{login}/".format(version=self.API_VERSION, login=login)
        admin_headers = self.get_authorization_headers("superuser")
        user_info_response = self.client.get(user_retrieve_path, **admin_headers)
        actual_file = self.assert_database(user_info_response)
        self.assertEquals(actual_file, desired_file, "The avatar has been attached to the wrong profile")

    def get_request_path(self):
        """
        Calculates the request uploading path

        :return: the request uploading path
        """
        return "/api/{version}/profile/avatar/".format(version=self.API_VERSION)

    def get_delete_path(self, updated_response):
        """
        Returns path of the DELETE response

        :param updated_response: the response on file updating request
        :return: path of the updating response
        """
        return self.get_request_path()

    def get_entity_detail_path(self, lookup):
        """
        Returns path for the entity detail requests (GET => get entity info, PUT, PATCH => set entity info,
            DELETE => delete the entity)

        :param: lookup Entity ID or alias
        :return: entity path
        """
        return "/api/{version}/profile/".format(version=self.API_VERSION)


del AvatarUploadTest
