from rest_framework import status

from ..base_view_test import BaseViewTest
from .synchronization_client import SynchronizationClient


class TestSynchronization(BaseViewTest):
    """
    Provides all synchronization test
    """

    superuser_required = True
    ordinary_user_required = True

    synchronization_path = "/api/{version}/account-synchronization/".format(version=BaseViewTest.API_VERSION)

    def test_synchronization_no_auth(self):
        """
        Tests whether synchronization process can be performed by a non-authorized user

        :return: nothing
        """
        response = self.client.get(self.synchronization_path)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED, "Unexpected status code")

    def test_synchronization_forbidden(self):
        """
        Tests whether synchronization is forbidden for ordinary users

        :return: nothing
        """
        headers = self.get_authorization_headers("ordinary_user")
        response = self.client.get(self.synchronization_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, "Unexpected status code")

    def test_synchronization_teapot(self):
        """
        Tests whether the user can perform synchronization when all synchronization modules were switched off

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.get(self.synchronization_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_418_IM_A_TEAPOT, "unexpected status code")

    def test_synchronization_success(self):
        """
        Provides a successful synchronization

        :return: nothing
        """
        self.enable_synchronization_module()
        sync_client = SynchronizationClient(self.client, self, self.get_authorization_headers("superuser"))
        sync_client.synchronize()

    def enable_synchronization_module(self):
        """
        Enables the synchronization module

        :return: nothing
        """
        from core.synchronizations.ihna_employees import IhnaSynchronization
        sync = IhnaSynchronization()
        sync.is_enabled = True
        sync.update()


del BaseViewTest
