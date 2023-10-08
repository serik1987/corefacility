from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from ....entity.corefacility_module import CorefacilityModuleSet
from ....entry_points import AuthorizationsEntryPoint, ProjectsEntryPoint, \
    SynchronizationsEntryPoint

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
        self._test_unpaginated_list({"profile": profile}, login, response_status)

    @parameterized.expand([
        (AuthorizationsEntryPoint, "superuser", status.HTTP_200_OK),
        (ProjectsEntryPoint, "superuser", status.HTTP_200_OK),
        (SynchronizationsEntryPoint, "superuser", status.HTTP_200_OK),
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
        self._test_unpaginated_list({"profile": "basic", "entry_point": entry_point_id}, login, response_status)

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
        self._container.is_application = True
        self._container.is_enabled = True
        self._test_unpaginated_list({"profile": "basic", "enabled_apps_only": ""}, login, status_code)

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
