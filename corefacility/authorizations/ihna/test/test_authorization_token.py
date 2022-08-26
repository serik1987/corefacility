from django.test import TestCase

from core.entity.user import User
from core.entity.entity_providers.posix_providers.posix_provider import PosixProvider
from core.entity.entity_providers.file_providers.files_provider import FilesProvider
from authorizations.ihna.entity import AuthorizationToken
from authorizations.ihna.entity.authorization_token.mock_provider import MockProvider


class TestAuthorizationToken(TestCase):
    """
    Tests the ihna.ru authorization token
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        PosixProvider.force_disable = True
        FilesProvider.force_disable = True
        User(login="sergei.kozhukhov").create()

    @classmethod
    def tearDownClass(cls):
        PosixProvider.force_disable = False
        FilesProvider.force_disable = False
        super().tearDownClass()

    def test_token_create(self):
        token = AuthorizationToken(code=MockProvider.generate_mock_code("authorization code"))
        self.assertEquals(token.state, "creating", "The token is initialized with valid state")
        self.assertIsNone(token.authentication, "The token authentication is not empty before create")

    def test_token_issue(self):
        token = AuthorizationToken(code=MockProvider.generate_mock_code("authorization code"))
        token.create()
        self.assertEquals(token.state, "saved",
                          "The authorization token doesn't turn into 'saved' after its create")
        self.assertIsNotNone(token.authentication, "Authentication was not assigned to the token during save")

    def _check_fields_changed(self, entity, field_list):
        """
        Checks whether the certain and only certain fields in the entity was changed

        :param entity: the entity to test
        :param field_list: field list to check in the entity object
        :return: nothing
        """
        pass
