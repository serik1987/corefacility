from rest_framework import status

from core.entity.user import User, UserSet
from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.entry_points.authorizations import AuthorizationModule

from ..base_view_test import BaseViewTest
from .synchronization_client import SynchronizationClient


class TestSynchronization(BaseViewTest):
    """
    Provides all synchronization test
    """

    superuser_required = True
    ordinary_user_required = True
    support_token = None

    synchronization_path = "/api/{version}/account-synchronization/".format(version=BaseViewTest.API_VERSION)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        support = UserSet().get("support")
        cls.support_token = AuthorizationModule.issue_token(support)

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

    def test_synchronization_partial_fail(self):
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
        self.assertEquals(sync_client.details[0]['action'], "remove",
                          "The error must be occured during the user remove")
        user_set = UserSet()
        user = user_set.get("superuser")
        self.assertEquals(user.name, "Superuser", "The user name must be saved intact")
        self.assertEquals(user.surname, "Superuserov", "The user surname must be saved intact")
        self.assertGreater(len(user_set), 10, "The users shall be added and downloaded successfully")
        user_set.get("support")
        with self.assertRaises(EntityNotFoundException,
                               msg="Ordinary user shall be removed successfully"):
            user_set.get("user")

    def test_synchronization_success(self):
        user = User(login="leonid.alexandrov", name="Иван", surname="Иванов")
        user.create()
        self.enable_synchronization_module()
        sync_client = SynchronizationClient(self.client, self, {
            "HTTP_AUTHORIZATION": "Token %s" % self.support_token
        })
        sync_client.synchronize()
        for user in UserSet():
            print("{id}\t{login}\t{name}\t{surname}".format(
                id=user.id,
                login=user.login,
                name=user.name,
                surname=user.surname
            ))

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
