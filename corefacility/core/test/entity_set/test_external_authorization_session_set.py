from parameterized import parameterized

from core.test.data_providers.entity_sets import filter_data_provider

from .base_test_class import BaseTestClass
from .entity_set_objects.external_authorization_session_set_object import ExternalAuthorizationSessionSetObject, \
    GoogleApp, IhnaApp, StandardAuthorization


def base_search_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 10, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 11, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (3, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (-1, 7, None), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (6, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (7, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (10, 20, None), BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),
    ]


def filter_authorization_module_provider():
    return filter_data_provider(
        (GoogleApp(), IhnaApp(), StandardAuthorization()),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        ]
    )


class TestExternalAuthorizationSessionSet(BaseTestClass):

    _external_authorization_session_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._external_authorization_session_set_object = ExternalAuthorizationSessionSetObject()

    def setUp(self):
        self._container = self._external_authorization_session_set_object.clone()
        self.initialize_filters()

    @parameterized.expand(base_search_provider())
    def test_base_search(self, feature_index, arg, test_type):
        """
        Tests all entity reading features

        :param feature_index: entity reading feature to test:
            0 - search by ID
            1 - search by alias
            2 - search by item index in the entity set
            3 - slicing
            4 - iterating
            5 - counting entity number
        :param arg: depends on testing feature:
            for searching by ID: entity index within the entity set object
            for searching by alias: entity alias
            for searching by item index: item index
            for slicing: a tuple containing start and stop indices and slice step
            for iteration: useless
            for entity counting: useless
        :param test_type: 0 for positive test, 1 for negative test, useless for iteration and counting
        :return: nothing
        """
        with self.assertLessQueries(1):
            self._test_all_access_features(feature_index, arg, test_type)

    @parameterized.expand(filter_authorization_module_provider())
    def test_filter_authorization_module(self, authorization_module, *args):
        self.apply_filter("authorization_module", authorization_module)
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertIs(actual_entity.authorization_module, expected_entity.authorization_module,
                      msg + ". The authorization module did not reproduced correctly")
        self.assertEquals(actual_entity.authorization_module.state, "loaded",
                          msg + ". The authorization module was not automatically loaded during the authorization "
                                "session retrieve")
