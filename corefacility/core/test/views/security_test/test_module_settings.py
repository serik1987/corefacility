from django.utils.duration import duration_string
from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from core import App as CoreApp
from imaging import App as ImagingApp
from roi import App as RoiApp

from .base_test_class import BaseTestClass


class TestModuleSettings(BaseTestClass):
    """
    Tests the core module settings.
    """

    core_application_uuid = None

    resource_name = "settings"
    superuser_required = True
    ordinary_user_required = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.core_application_uuid = str(CoreApp().uuid)
        cls.imaging_application_uuid = str(ImagingApp().uuid)
        cls.roi_application_uuid = str(RoiApp().uuid)

    @parameterized.expand([
        ("superuser", status.HTTP_200_OK),
        ("ordinary_user", status.HTTP_403_FORBIDDEN),
        (None, status.HTTP_401_UNAUTHORIZED)
    ])
    def test_default_values(self, token_id, response_status):
        """
        Tests application settings retrieval
        """
        path = self.get_entity_detail_path(self.core_application_uuid)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")
        if response_status == status.HTTP_200_OK:
            self.assert_same(response.data)

    @parameterized.expand([("4a3e2e44-8eef-4ae0-9016-54b7eaa770ca",), ("invalid uuid",), ("",)])
    def test_fake_module_settings(self, module_uuid):
        path = self.get_entity_detail_path(module_uuid)
        headers = self.get_authorization_headers("superuser")
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND, "Fake resource found")

    def assert_same(self, actual_data):
        CoreApp.reset()
        app = CoreApp()
        if 'uuid' in actual_data:
            self.assertEquals(actual_data['uuid'], str(app.uuid), "Module UUID has not been retrieved")
        if 'name' in actual_data:
            self.assertEquals(actual_data['name'], gettext(app.name), "Module name has not been retrieved")
        if 'max_password_symbols' in actual_data:
            self.assertEquals(actual_data['max_password_symbols'],
                              app.get_max_password_symbols(),
                              "Wrong number of maximum password symbols in the module")
        self.assertEquals(actual_data['auth_token_lifetime'], duration_string(app.get_auth_token_lifetime()),
                          "Wrong value of the authorization token lifetime")
        self.assertEquals(actual_data['is_user_can_change_password'], app.user_can_change_password(),
                          "Wrong value of the 'is_user_can_change_password' field")
