from rest_framework import status
from parameterized import parameterized

from .base_test_class import BaseTestClass
from .data_providers import arbitrary_string_provider


class TestGroup(BaseTestClass):
    """
    Checks the validity of the group fields
    """

    empty_data = {}
    standard_data = {"name": "Оптическое картирование"}
    another_data = {"name": "Вазомоторные колебания"}

    resource_name = "groups"

    def test_name_required(self):
        self._test_field_required("name", "empty", True, True, "Some group name")

    @parameterized.expand(arbitrary_string_provider(False, 256))
    def test_name(self, group_name, is_valid):
        self._test_field_value("name", "empty", group_name, is_valid, True, group_name)

    def test_name_create_duplication(self):
        headers = self.get_authorization_headers("superuser")
        create_response = self.client.post(self.get_entity_list_path(),
                                           data=self.standard_data, format="json", **headers)
        self.assertEquals(create_response.status_code, status.HTTP_201_CREATED, "Unexpected response code")
        another_response = self.client.post(self.get_entity_list_path(),
                                            data=self.standard_data, format="json", **headers)
        self.assertEquals(another_response.status_code, status.HTTP_400_BAD_REQUEST, "Unexpected response code")
        self.assertEquals(another_response.data['code'], "EntityDuplicatedException",
                          "Unexpected error code")

    def test_name_modify_duplication(self):
        headers = self.get_authorization_headers("superuser")
        create_entity_1 = self.client.post(self.get_entity_list_path(),
                                           data=self.standard_data, format="json", **headers)
        self.assertEquals(create_entity_1.status_code, status.HTTP_201_CREATED, "Unexpected response code")
        create_entity_2 = self.client.post(self.get_entity_list_path(),
                                           data=self.another_data, format="json", **headers)
        self.assertEquals(create_entity_2.status_code, status.HTTP_201_CREATED, "Unexpected response code")
        update_path = self.get_entity_detail_path(create_entity_2.data['id'])
        update_response = self.client.patch(update_path, data=self.standard_data, format="json", **headers)
        self.assertEquals(update_response.status_code, status.HTTP_400_BAD_REQUEST, "Unexpected response code")
        self.assertEquals(update_response.data['code'], 'EntityDuplicatedException', "YUnexpected error code")
        print(update_response.data)

    def test_governor_read_only(self):
        self._test_read_only_field("name", "standard", None)
