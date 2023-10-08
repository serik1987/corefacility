from random import choice

from rest_framework import status
from parameterized import parameterized

from ....entity.entity_sets.user_set import UserSet

from .avatar_upload_test import AvatarUploadTest


class TestUserAvatarUpload(AvatarUploadTest):
    """
    Provides testing routines for the avatar upload
    """

    resource_name = "users"
    resource_id = None
    entity_set_class = UserSet

    def tearDown(self):
        self.resource_id = None
        super().tearDown()

    @parameterized.expand([
        (None, status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", status.HTTP_403_FORBIDDEN),
        ("superuser", status.HTTP_200_OK),
    ])
    def test_security(self, token_id, expected_status_code):
        self._test_security(token_id, expected_status_code)

    def get_random_resource_id(self):
        """
        Returns a random resource ID

        :return: a random resource ID
        """
        if self.resource_id is None:
            self.resource_id = choice(("user", "superuser"))
        return self.resource_id


del AvatarUploadTest
