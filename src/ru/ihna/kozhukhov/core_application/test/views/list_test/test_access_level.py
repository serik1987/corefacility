from rest_framework import status
from parameterized import parameterized

from ...entity_set.test_access_level_set import LANGUAGE_CODES

from .base_test_class import BaseTestClass


# noinspection PyTypeChecker
def search_detail_provider():
    return [
        (*authorization_args, *expected_dataset_args)
        for authorization_args in [
            ("ordinary_user", status.HTTP_200_OK),
            (None, status.HTTP_401_UNAUTHORIZED),
        ]
        for expected_dataset_args in LANGUAGE_CODES
    ] + [
        ("ordinary_user", status.HTTP_400_BAD_REQUEST, "ru-RU", -1, "unknown", None),
    ]


class TestAccessLevel(BaseTestClass):
    """
    Test routines for the access level lists
    """

    LEVEL_ALIAS_INDEX = 0

    superuser_required = False
    ordinary_user_required = True
    _request_path = "/api/{version}/access-levels/".format(version=BaseTestClass.API_VERSION)

    def test_search_general(self):
        """
        Provides general search for the access level set

        :return: nothing
        """
        headers = self.get_authorization_headers("ordinary_user")
        response = self.client.get(self.request_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    @parameterized.expand(search_detail_provider())
    def test_search_detail(self, token_id, expected_status_code, lang, lang_index, level_type, expected_level_set):
        """
        Provides detailed search for the access level set

        :param token_id: token ID corresponding to the authorized user
        :param expected_status_code: expected response status code
        :param lang: expected language
        :param lang_index: index of the expected dataset within the expected_set tuple
        :param level_type: expected level type
        :param expected_level_set: expected level set name
        :return: nothing
        """
        with self.settings(LANGUAGE_CODE=lang):
            headers = self.get_authorization_headers(token_id)
            query_params = {"type": level_type}
            response = self.client.get(self.request_path, query_params, **headers)
            self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")
            if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
                self.assertEquals(len(response.data), len(expected_level_set))
                for level_index in range(len(response.data)):
                    actual_level_info = response.data[level_index]
                    expected_level_info = expected_level_set[level_index]
                    self.assertEquals(actual_level_info['type'], level_type, "Unexpected level type")
                    self.assertEquals(actual_level_info['alias'], expected_level_info[self.LEVEL_ALIAS_INDEX],
                                      "Unexpected level alias")
                    self.assertEquals(actual_level_info['name'], expected_level_info[lang_index],
                                      "Unexpected level name")
