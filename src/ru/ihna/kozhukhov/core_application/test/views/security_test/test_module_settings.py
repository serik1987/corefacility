from django.utils.duration import duration_string
from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from .... import App as CoreApp

from .base_test_class import BaseTestClass


class TestModuleSettings(BaseTestClass):
    """
    Tests the core module settings.
    """

    core_application_uuid = None
    imaging_application_uuid = None
    roi_application_uuid = None

    resource_name = "settings"
    superuser_required = True
    ordinary_user_required = True

    default_data = {
        "is_enabled": True,
        "max_password_symbols": 8,
        "auth_token_lifetime": "01:00:00",
        "is_user_can_change_password": True,
    }

    half_set_data = {
        "max_password_symbols": 12,
        "is_user_can_change_password": True,
    }

    another_half_set_data = {
        "max_password_symbols": 8,
        "auth_token_lifetime": "01:00:00",
    }

    app_data = {
        "is_enabled": False,
        "permissions": "permission_required",
    }

    app_half_data = {"is_enabled": False}
    app_another_half_data = {"permissions": "permission_required"}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.core_application_uuid = str(CoreApp().uuid)

    @parameterized.expand([
        ("superuser", status.HTTP_200_OK),
        ("ordinary_user", status.HTTP_403_FORBIDDEN),
        (None, status.HTTP_401_UNAUTHORIZED)
    ])
    def test_default_values(self, token_id, response_status):
        """
        Tests whether core module settings can be downloaded
        """
        path = self.get_entity_detail_path(self.core_application_uuid)
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")
        if response_status == status.HTTP_200_OK:
            self.assert_same(response.data)
            CoreApp.reset()
            self.assert_same(response.data)

    @parameterized.expand([
        ("imaging", "superuser", status.HTTP_200_OK),
        ("roi", "superuser", status.HTTP_200_OK),
        ("imaging", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("imaging", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_apps_default_value(self, app_name, login, response_status):
        """
        Tests default values for all applications
        """
        app_uuid = getattr(self, "%s_application_uuid" % app_name)
        app_settings_path = self.get_entity_detail_path(app_uuid)
        headers = self.get_authorization_headers(login)
        response = self.client.get(app_settings_path, **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected status code")
        if response_status == status.HTTP_200_OK:
            self.assert_app_same(response.data, app_name)
            self.all_apps[app_name].reset()
            self.assert_app_same(response.data, app_name)

    @parameterized.expand([("4a3e2e44-8eef-4ae0-9016-54b7eaa770ca",), ("invalid uuid",), ("",)])
    def test_fake_module_settings(self, module_uuid):
        """
        Negative test cases under the condition when module's UUID in the module path is not valid
        """
        path = self.get_entity_detail_path(module_uuid)
        headers = self.get_authorization_headers("superuser")
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND, "Fake resource found")

    @parameterized.expand([
        ("superuser", "default", "put", status.HTTP_200_OK),
        ("superuser", "half_set", "patch", status.HTTP_200_OK),
        ("ordinary_user", "default", "put", status.HTTP_403_FORBIDDEN),
        (None, "default", "put", status.HTTP_401_UNAUTHORIZED),
    ])
    def test_module_update(self, login, dataset, update_method, response_status):
        """
        Checks whether the user can update the module
        """
        update_function = getattr(self.client, update_method)
        path = self.get_entity_detail_path(self.core_application_uuid)
        headers = self.get_authorization_headers(login)
        data = getattr(self, "%s_data" % dataset)
        response = update_function(path, data, format="json", **headers)
        self.assertEquals(response.status_code, response_status, "Unexpected response status")
        if response.status_code == status.HTTP_200_OK:
            self.assert_same(data, check_integrity=False)
            another_response = self.client.get(path, **headers)
            self.assertEquals(another_response.status_code, status.HTTP_200_OK,
                              "The data have been crushed after their update and has no longer been downloadable")
            CoreApp.reset()
            self.assert_same(data, check_integrity=False)
            another_response = self.client.get(path, **headers)
            self.assertEquals(another_response.status_code, status.HTTP_200_OK,
                              "The data have been crushed after their update and has no longer been downloadable")
            self.assert_same(another_response.data, check_integrity=True)

    @parameterized.expand([
        ("put", "app", "imaging", "superuser", status.HTTP_200_OK),
        ("put", "app", "roi", "superuser", status.HTTP_200_OK),
        ("patch", "app_half", "roi", "superuser", status.HTTP_200_OK),
        ("patch", "app_another_half", "roi", "superuser", status.HTTP_200_OK),
        ("put", "app", "imaging", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("patch", "app_half", "roi", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_application_update(self, update_method, data, app, login, expected_status):
        """
        Checks the user can update applications
        """
        app_class = self.all_apps[app]
        uuid = getattr(self, "%s_application_uuid" % app)
        update_function = getattr(self.client, update_method)
        path = self.get_entity_detail_path(uuid)
        data = getattr(self, "%s_data" % data)
        headers = self.get_authorization_headers(login)
        response = update_function(path, data, format="json", **headers)
        self.assertEquals(response.status_code, expected_status, "Unexpected response status during the update")
        if response.status_code == status.HTTP_200_OK:
            self.assert_app_same(response.data, app, check_integrity=(update_method == "PUT"))
            self.assert_app_same(data, app, check_integrity=False)
            another_response = self.client.get(path, **headers)
            self.assertEquals(another_response.status_code, status.HTTP_200_OK, "Unexpected retrieve response status")
            self.assert_app_same(another_response.data, app)
            app_class.reset()
            self.assert_app_same(data, app, check_integrity=False)

    def test_incremental_update(self):
        """
        Tests whether several consecutive updates are independent on each other
        """
        path = self.get_entity_detail_path(self.core_application_uuid)
        headers = self.get_authorization_headers("superuser")
        pr1 = self.client.patch(path, data=self.half_set_data, format="json", **headers)
        self.assertEquals(pr1.status_code, status.HTTP_200_OK, "Unexpected status code")
        pr2 = self.client.patch(path, data=self.another_half_set_data, format="json", **headers)
        self.assertEquals(pr2.status_code, status.HTTP_200_OK, "Unexpected status code")
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected response code")
        self.assert_same(response.data)
        CoreApp.reset()
        self.assert_same(response.data)
        default_data = self.default_data.copy()
        default_data['uuid'] = response.data['uuid']
        default_data['name'] = response.data['name']
        self.assert_same(default_data)

    @parameterized.expand([("imaging",), ("roi",)])
    def test_app_incremental_update(self, app_name):
        app = self.all_apps[app_name]()
        path = self.get_entity_detail_path(str(app.uuid))
        headers = self.get_authorization_headers("superuser")
        pr1 = self.client.patch(path, self.app_half_data, format="json", **headers)
        self.assertEquals(pr1.status_code, status.HTTP_200_OK, "Unexpected status code")
        pr2 = self.client.patch(path, self.app_another_half_data, format="json", **headers)
        self.assertEquals(pr2.status_code, status.HTTP_200_OK, "Unexpected status code")
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
        default_data = self.app_data.copy()
        default_data['uuid'] = str(app.uuid)
        default_data['name'] = gettext(app.name)
        self.assert_app_same(default_data, app_name)

    def assert_same(self, actual_data, check_integrity=True):
        if check_integrity:
            self.assertIn('uuid', actual_data, "The field is missed in the output data")
            self.assertIn('name', actual_data, "The field is missed in the output data")
            self.assertIn('max_password_symbols', actual_data, "The field is missed in the output data")
            self.assertIn('auth_token_lifetime', actual_data, "The field is missed in the output data")
            self.assertIn('is_user_can_change_password', actual_data, "The field is missed in the output data")
        app = CoreApp()
        if 'uuid' in actual_data:
            self.assertEquals(actual_data['uuid'], str(app.uuid), "Module UUID has not been retrieved")
        if 'name' in actual_data:
            self.assertEquals(actual_data['name'], gettext(app.name), "Module name has not been retrieved")
        if 'max_password_symbols' in actual_data:
            self.assertEquals(actual_data['max_password_symbols'],
                              app.get_max_password_symbols(),
                              "Wrong number of maximum password symbols in the module")
        if 'auth_token_lifetime' in actual_data:
            self.assertEquals(actual_data['auth_token_lifetime'], duration_string(app.get_auth_token_lifetime()),
                              "Wrong value of the authorization token lifetime")
        self.assertEquals(actual_data['is_user_can_change_password'], app.user_can_change_password(),
                          "Wrong value of the 'is_user_can_change_password' field")

    def assert_app_same(self, actual_data, app_name, check_integrity=True):
        if check_integrity:
            self.assertIn('uuid', actual_data, "No 'uuid' in the data")
            self.assertIn('name', actual_data, "No 'name' in the data")
            self.assertIn('is_enabled', actual_data, "No 'is_enabled' in the data")
            self.assertIn('permissions', actual_data, "No 'permissions' in the data")
        app = self.all_apps[app_name]()
        if 'uuid' in actual_data:
            self.assertEquals(actual_data['uuid'], str(app.uuid), "Bad application UUID")
        if 'name' in actual_data:
            self.assertEquals(actual_data['name'], gettext(app.name), "Bad application name")
        if 'is_enabled' in actual_data:
            self.assertEquals(actual_data['is_enabled'], app.is_enabled, "Bad application enability")
        if 'permissions' in actual_data:
            self.assertEquals(actual_data['permissions'], app.permissions, "Bad permission level")
