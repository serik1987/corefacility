from datetime import datetime, timedelta
from parameterized import parameterized

from core.entity.user import User
from core.entity.authentication import Authentication
from core.test.entity.base_external_authorization_token import TestExternalAuthorizationToken

from .authorization_token_object import AuthorizationTokenObject


class TestAuthorizationToken(TestExternalAuthorizationToken):
    """
    Tests the external authorizations
    """

    EXPIRATION_TIME = timedelta(milliseconds=300)

    _entity_object_class = AuthorizationTokenObject

    _sample_user = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._sample_user = User(login="sergei.kozhukhov")
        cls._sample_user.create()

    @parameterized.expand([
        ("access_token", "iugh789reh7834hh", ValueError),
        ("expires_in", datetime.now(), ValueError),
        ("refresh_token", "zdhfbbobigfnb", ValueError),
    ])
    def test_read_only_field(self, field_name, sample_value, throwing_exception):
        self._test_read_only_field(field_name, sample_value, throwing_exception)

    def test_authentication_read_only(self):
        auth = Authentication(user=self._sample_user)
        auth.token_hash.generate(auth.token_hash.ALL_SYMBOLS, auth.TOKEN_PASSWORD_SIZE)
        auth.expiration_date.set(self.EXPIRATION_TIME)
        auth.create()
        self._test_read_only_field("authentication", auth, ValueError)

    def _do_entity_update(self, obj):
        obj.change_entity_fields()

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


del TestExternalAuthorizationToken
