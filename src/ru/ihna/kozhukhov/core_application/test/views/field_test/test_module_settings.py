from datetime import timedelta
from django.utils.duration import duration_string
from rest_framework import status
from parameterized import parameterized

from .... import App as CoreApp

from .base_test_class import BaseTestClass


class TestModuleSettings(BaseTestClass):
    """
    Provides field test for the core application
    """

    apps = None
    resource_name = "settings"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.apps = dict()
        cls.apps['core'] = CoreApp

    @parameterized.expand([
        ('core', 'is_enabled', False, status.HTTP_200_OK, True),
        ('core', 'is_enabled', True, status.HTTP_200_OK, True),
        ('core', 'max_password_symbols', 5, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'max_password_symbols', 6, status.HTTP_200_OK, None),
        ('core', 'max_password_symbols', 20, status.HTTP_200_OK, None),
        ('core', 'max_password_symbols', 1024, status.HTTP_200_OK, None),
        ('core', 'max_password_symbols', "hello", status.HTTP_400_BAD_REQUEST, None),
        ('core', 'max_password_symbols', True, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'max_password_symbols', 3.14, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'auth_token_lifetime', '00:05:00', status.HTTP_200_OK, None),
        ('core', 'auth_token_lifetime', '00:04:59', status.HTTP_400_BAD_REQUEST, None),
        ('core', 'auth_token_lifetime', 'fake duration', status.HTTP_400_BAD_REQUEST, None),
        ('core', 'auth_token_lifetime', 42, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'auth_token_lifetime', 3.14, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'auth_token_lifetime', True, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'is_user_can_change_password', True, status.HTTP_200_OK, None),
        ('core', 'is_user_can_change_password', False, status.HTTP_200_OK, None),
        ('core', 'is_user_can_change_password', 'fake', status.HTTP_400_BAD_REQUEST, None),
        ('core', 'is_user_can_change_password', 80, status.HTTP_400_BAD_REQUEST, None),
        ('core', 'is_user_can_change_password', 3.14, status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'is_enabled', False, status.HTTP_200_OK, None),
        ('imaging', 'is_enabled', True, status.HTTP_200_OK, None),
        ('imaging', 'is_enabled', 'fake', status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'is_enabled', 80, status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'is_enabled', 3.14, status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'permissions', 'add', status.HTTP_200_OK, None),
        ('imaging', 'permissions', 'permission_required', status.HTTP_200_OK, None),
        ('imaging', 'permissions', 'fake', status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'permissions', True, status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'permissions', 0, status.HTTP_400_BAD_REQUEST, None),
        ('imaging', 'permissions', 0.8, status.HTTP_400_BAD_REQUEST, None),
    ])
    def test_field(self, app_name, name, value, expected_status_code, expected_value):
        """
        Tests various settings fields for valid and non-valid values
        :param app_name: testing application name
        :param name: field name
        :param value: field value
        :param expected_status_code: status code to be expected to send
        :param expected_value: value that shall be actually set or None if this is the same as the value. Ignored for
            4xx responses
        """
        path = self.get_entity_detail_path(self.apps[app_name]().uuid)
        data = {name: value}
        headers = self.get_authorization_headers("superuser")
        response = self.client.patch(path, data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response code")
        if expected_status_code == status.HTTP_200_OK:
            if expected_value is not None:
                value = expected_value
            self.assertEquals(response.data[name], value, "The field is not present in the response body")
            self.assert_field_exists(self.apps[app_name](), name, value)
            self.apps[app_name].reset()
            self.assert_field_exists(self.apps[app_name](), name, value)

    def assert_field_exists(self, app, name, value):
        if name == 'is_enabled':
            self.assertEquals(app.is_enabled, value, "The field was not properly delivered to the module")
        else:
            actual_value = app.user_settings.get(name)
            if isinstance(actual_value, timedelta):
                actual_value = duration_string(actual_value)
            self.assertEquals(actual_value, value, "The field was not properly delivered to the module")
