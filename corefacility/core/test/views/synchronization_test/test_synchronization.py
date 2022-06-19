from rest_framework import status

from core.entity.user import UserSet

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
        response = self.client.post(self.synchronization_path)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED, "Unexpected status code")

    def test_synchronization_forbidden(self):
        """
        Tests whether synchronization is forbidden for ordinary users

        :return: nothing
        """
        headers = self.get_authorization_headers("ordinary_user")
        response = self.client.post(self.synchronization_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN, "Unexpected status code")

    def test_synchronization_teapot(self):
        """
        Tests whether the user can perform synchronization when all synchronization modules were switched off

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.post(self.synchronization_path, **headers)
        self.assertEquals(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE, "unexpected status code")

    def test_synchronization_success(self):
        """
        Tests whether synchronization shall be successful when one of the synchronizing users is currently logged ins

        :return: nothing
        """
        self.enable_synchronization_module()
        sync_client = SynchronizationClient(self.client, self, self.get_authorization_headers("superuser"))
        sync_client.synchronize()
        self.assertEquals(len(sync_client.details), 1, "There must be one error")
        self.assertEquals(sync_client.details[0]['login'], "superuser", "The error must be about the superuser")
        self.assertEquals(sync_client.details[0]['name'], "Superuser", "The user's name must be 'superuser'")
        self.assertEquals(sync_client.details[0]['surname'], "Superuserov", "The user's surname must be 'Superuserov'")

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
