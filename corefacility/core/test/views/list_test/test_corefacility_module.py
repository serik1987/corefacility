from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from core.entity.corefacility_module import CorefacilityModuleSet
from core.entity.entry_points import AuthorizationsEntryPoint, SettingsEntryPoint, ProjectsEntryPoint, \
    SynchronizationsEntryPoint
from imaging.entity.entry_points import ProcessorsEntryPoint
from core import App as CoreApp
from imaging import App as ImagingApp
from roi import App as RoiApp

from .base_test_class import BaseTestClass


class TestCorefacilityModule(BaseTestClass):
    """
    Provides list test for the corefacility modules
    """

    _request_path = "/api/{version}/settings/".format(version=BaseTestClass.API_VERSION)
    ep_list_path = "/api/{version}/settings/{module}/entry-points/"

    superuser_required = True
    ordinary_user_required = True

    def setUp(self):
        super().setUp()
        self._container = CorefacilityModuleSet()

    @parameterized.expand([
        ("basic", "superuser", status.HTTP_200_OK),
        ("light", "superuser", status.HTTP_200_OK),
        ("basic", "ordinary_user", status.HTTP_403_FORBIDDEN),
        ("basic", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_base_search(self, profile, login, response_status):
        """
        Basic search test
        """
        self._test_search({"profile": profile}, login, response_status)

    @parameterized.expand([
        (AuthorizationsEntryPoint, "superuser", status.HTTP_200_OK),
        (SettingsEntryPoint, "superuser", status.HTTP_200_OK),
        (ProjectsEntryPoint, "superuser", status.HTTP_200_OK),
        (SynchronizationsEntryPoint, "superuser", status.HTTP_200_OK),
        (ProcessorsEntryPoint, "superuser", status.HTTP_200_OK),
        (None, "superuser", status.HTTP_200_OK),
        ("fake-entry-point", "superuser", status.HTTP_400_BAD_REQUEST),
        (AuthorizationsEntryPoint, "ordinary_user", status.HTTP_403_FORBIDDEN),
        (AuthorizationsEntryPoint, None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_search_entry_point(self, entry_point_class, login, response_status):
        """
        Tests the entry point filter
        """
        if isinstance(entry_point_class, type):
            entry_point = entry_point_class()
            self._container.entry_point = entry_point
            entry_point_id = str(entry_point.id)
        elif isinstance(entry_point_class, str):
            entry_point_id = entry_point_class
        else:
            self._container.is_root_module = True
            entry_point_id = ""
        self._test_search({"profile": "basic", "entry_point": entry_point_id}, login, response_status)

    @parameterized.expand([
        (True, True, "superuser", status.HTTP_200_OK),
        (True, False, "superuser", status.HTTP_200_OK),
        (False, True, "superuser", status.HTTP_200_OK),
        (False, False, "superuser", status.HTTP_200_OK),
        (True, True, "ordinary_user", status.HTTP_200_OK),
        (True, True, None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_enabled_apps_only(self, imaging_app_enabled, roi_app_enabled, login, status_code):
        """
        Tests the 'enabled apps only' filter
        """
        if not imaging_app_enabled:
            imaging_app = ImagingApp()
            imaging_app.is_enabled = False
            imaging_app.update()
        if not roi_app_enabled:
            roi_app = RoiApp()
            roi_app.is_enabled = False
            roi_app.update()
        self._container.is_application = True
        self._container.is_enabled = True
        self._test_search({"profile": "basic", "enabled_apps_only": ""}, login, status_code)

    @parameterized.expand([
        (CoreApp, "superuser", status.HTTP_200_OK),
        (ImagingApp, "superuser", status.HTTP_200_OK),
        (RoiApp, "superuser", status.HTTP_200_OK),
        (CoreApp, "ordinary_user", status.HTTP_403_FORBIDDEN),
        (CoreApp, None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entry_points(self, module_class, login, expected_status_code):
        """
        Tests all entry points
        """
        module = module_class()
        path = self.ep_list_path.format(version=self.API_VERSION, module=module.uuid)
        headers = self.get_authorization_headers(login)
        response = self.client.get(path, **headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status")
        if expected_status_code == status.HTTP_200_OK:
            results = response.data['results']
            self.assertEquals(len(results), len(module.get_entry_points()), "Unexpected number of entry points")
            for entry_point_info in results:
                self.assertIn(entry_point_info['alias'], module.get_entry_points(),
                              "Entry point '%s' is not within the list" % entry_point_info['alias'])
                entry_point = module.get_entry_points()[entry_point_info['alias']]
                self.assertEquals(entry_point_info['id'], entry_point.id, "Unexpected entry point ID")
                self.assertEquals(entry_point_info['name'], gettext(entry_point.name), "Unexpected entry point name")

    def assert_items_equal(self, response_info, module):
        """
        Asserts that correct module info has been sent to the client
        :param response_info: the module info sent to the client
        :param module: the module which info has been sent to the client
        :return: nothing
        """
        self.assertEquals(response_info['uuid'], str(module.uuid), "Unexpected response code")
        self.assertEquals(response_info['name'], gettext(module.name), "Unexpected module name")
        self.assertEquals(response_info['alias'], module.alias, "Unexpected module alias")
