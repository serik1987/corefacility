from parameterized import parameterized

from core.entity.user import User
from core.test.entity.base_external_authorization_token import TestExternalAuthorizationToken
from authorizations.google.entity import AuthorizationToken

from .authorization_token_object import AuthorizationTokenObject


class TestAuthorizationToken(TestExternalAuthorizationToken):
    """
    Tests the external authorization token.
    """

    _sample_user = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._sample_user = User(login="sergei.kozhukhov")
        cls._sample_user.create()

    _entity_object_class = AuthorizationTokenObject

    @parameterized.expand(["access_token", "expires_in", "refresh_token"])
    def test_field_reloaded(self, field_name):
        obj = AuthorizationTokenObject()
        obj.create_entity()
        old_field = getattr(obj.entity, field_name)
        obj.reload_entity()
        new_field = getattr(obj.entity, field_name)
        self.assertEquals(old_field, new_field, "The field '%s' was not successfully reloaded" % field_name)

    def test_access_token_changed(self):
        obj = AuthorizationTokenObject()
        obj.create_entity()
        obj.reload_entity()
        token_before_refresh = obj.entity.access_token
        obj.entity.refresh_token.refresh()
        token_after_refresh = obj.entity.access_token
        self.assertNotEqual(token_after_refresh, token_before_refresh, "The access token doesn't seem to be refreshed")
        obj.reload_entity()
        self.assertEquals(obj.entity.access_token, token_after_refresh,
                          "The access token doesn't properly saved to the database after refresh")

    def test_expires_in_changed(self):
        obj = AuthorizationTokenObject()
        obj.create_entity()
        obj.reload_entity()
        old_expires_in = obj.entity.expires_in
        obj.entity.refresh_token.refresh()
        new_expires_in = obj.entity.expires_in
        self.assertGreaterEqual(new_expires_in, old_expires_in,
                                "The access token was not successfully renewed according to the expiration date")
        obj.reload_entity()
        self.assertEquals(obj.entity.expires_in, new_expires_in,
                          "Token expiration date was not successfully reloaded after the access token refresh")

    def _check_default_fields(self, token):
        super()._check_default_fields(token)
        self.assertFieldReceived(token, "access_token")
        self.assertFieldReceived(token, "expires_in")

    def _check_default_change(self, token):
        super()._check_default_change(token)
        self.assertFieldReceived(token, "access_token")
        self.assertFieldReceived(token, "expires_in")

    def _check_changed_entity(self, entity, expected_id):
        """
        Checks whether the entity was changed

        :param entity: the entity to check
        :param expected_id: the entity ID to be expected
        :return: nothing
        """
        self.assertEquals(entity.id, expected_id, "The entity ID is not correct")
        self.assertEquals(entity.state, "saved",
                          "The entity state is not 'changed' after entity fields were corrected")
        self._check_default_change(entity)

    def _do_entity_update(self, obj):
        obj.entity.refresh_token.refresh()
        obj.notify_access_token_changed()

    def _check_fields_changed(self, entity, field_list):
        """
        Checks whether the certain and only certain fields in the entity was changed

        :param entity: the entity to test
        :param field_list: field list to check in the entity object
        :return: nothing
        """
        pass


del TestExternalAuthorizationToken
