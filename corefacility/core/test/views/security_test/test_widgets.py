from rest_framework import status
from parameterized import parameterized

from core import App as CoreApp
from core.test.data_providers.module_providers import entry_point_provider as base_entry_point_provider

from .base_test_class import BaseTestClass


def entry_point_provider():
    """
    Provides the data for the test_widgets_positive test function
    """
    permissions_table = [
        ("superuser", status.HTTP_200_OK),
        ("ordinary_user", status.HTTP_200_OK),
        (None, status.HTTP_200_OK),
    ]
    return [
        (data['entry_point'], token_id, expected_status_code)
        for data in base_entry_point_provider()
        for token_id, expected_status_code in permissions_table
    ]


def negative_entry_point_provider():
    """
    Provides the data for the test_widgets_negative test function
    """
    return [
        ("123e4567-e89b-12d3-a456-426655440000", "authorizations"),
        ("definitely-not-a-uuid", "authorizations"),
        (str(CoreApp().uuid), "fake_entry_point"),
    ]


class TestWidgets(BaseTestClass):
    """
    Provides testing for various widgets requests
    """

    WIDGET_LIST_PATH = "/api/{version}/widgets/%s/%s/".format(version=BaseTestClass.API_VERSION)

    superuser_required = True
    ordinary_user_required = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        CoreApp().reset()  # Because core module's UUID has been changed during the repeating migration

    @parameterized.expand(entry_point_provider())
    def test_widgets_normal(self, entry_point_class, token_id, expected_status_code):
        """
        Widget tests under normal conditions, i.e., with existent module UUID and entry point alias
        :param entry_point_class: entry point class that will be used to estimate module UUID and entry point alias
        :param token_id: token ID
        :param expected_status_code: response status code to be expected
        """
        entry_point = entry_point_class()
        module_uuid = entry_point.belonging_module.uuid
        widget_list_path = self.WIDGET_LIST_PATH % (module_uuid, entry_point.alias)
        auth_headers = self.get_authorization_headers(token_id)
        response = self.client.get(widget_list_path, **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        self.assert_result(response.data, entry_point.widgets(True))

    @parameterized.expand(negative_entry_point_provider())
    def test_widgets_negative(self, module_uuid, entry_point_alias):
        """
        Widget tests under negative conditions, i.e., when either module UUID or entry point alias don't exist
        :param module_uuid: module's UUID
        :param entry_point_alias: alias for the entry point
        """
        widget_list_path = self.WIDGET_LIST_PATH % (module_uuid, entry_point_alias)
        headers = self.get_authorization_headers("superuser")
        response = self.client.get(widget_list_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND, "Unexpected response status")

    def assert_result(self, actual_result, expected_result):
        expected_result = [
            {"uuid": str(uuid), "alias": alias, "name": name, "html_code": html_code}
            for uuid, alias, name, html_code in expected_result
        ]
        self.assertEquals(len(actual_result), len(expected_result), "Unexpected number of widgets")
        for n in range(len(actual_result)):
            actual_item = actual_result[n]
            expected_item = expected_result[n]
            for key, actual_value in actual_item.items():
                expected_value = expected_item[key]
                self.assertEquals(actual_value, expected_value, "Unexpected " + key)


del BaseTestClass
