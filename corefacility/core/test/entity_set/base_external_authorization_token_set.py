from parameterized import parameterized

from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject


class TestExternalAuthorizationTokenSet(BaseTestClass):
    """
    Provides base test routines for all external authorization tokens.
    """

    _token_set_object_class = None
    _token_set_class = None

    _user_set_object = None
    _token_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._token_set_object = cls._token_set_object_class()

    @property
    def user_set_object(self):
        return self._user_set_object

    @property
    def token_set_object(self):
        return self._token_set_object

    def setUp(self):
        super().setUp()
        self._container = self._token_set_object.clone()

    @parameterized.expand([
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 4, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 5, BaseTestClass.NEGATIVE_TEST_CASE),
    ])
    def test_general_token_list(self, feature_index, arg, test_type):
        with self.assertLessQueries(1):
            self._test_all_access_features(feature_index, arg, test_type)

    @parameterized.expand([(n,) for n in range(5)])
    def test_find_by_authentication(self, token_index):
        auth_token = self._token_set_object[token_index]
        authentication = auth_token.authentication
        auth_token_set = self._token_set_class()
        actual_token = auth_token_set.get(authentication)
        expected_token = auth_token_set[token_index]
        self.assertEntityFound(actual_token, expected_token,
                               "The authentication token was not retrieved correctly during looking by authentication")

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.authentication.id, expected_entity.authentication.id,
                          msg + ". Authentication IDs are not the same")


del BaseTestClass
