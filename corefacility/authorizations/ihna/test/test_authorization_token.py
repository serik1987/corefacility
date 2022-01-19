from django.test import TestCase

from core.entity.user import User
from authorizations.ihna.entity import AuthorizationToken
from authorizations.ihna.entity.authorization_token.mock_provider import MockProvider


class TestAuthorizationToken(TestCase):
    """
    Tests the ihna.ru authorization token
    """

    @classmethod
    def setUpTestData(cls):
        User(login="sergei.kozhukhov").create()

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
