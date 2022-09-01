from parameterized import parameterized

from core.test.entity_set.base_test_class import BaseTestClass

from imaging.tests.data_providers.entity_objects.map_set_object import MapSetObject


def base_search_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 5, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ALIAS, "c022_X210", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "c022_X100", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "c022_X300", BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (2, 4, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (2, 4, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, None, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (10, 20, None), BaseTestClass.POSITIVE_TEST_CASE),
    ]


def project_filter_provider():
    return [
        (project_index, *args)
        for project_index in range(2)
        for args in [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    ]


class TestMapSet(BaseTestClass):
    """
    Provides the map set testing
    """

    _imaging_map_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._imaging_map_object = MapSetObject()

    def setUp(self):
        super().setUp()
        self._container = self._imaging_map_object.clone()

    @parameterized.expand(base_search_provider())
    def test_all_access_features(self, *args):
        """
        Tests the basic imaging map iteration facility
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
            self._test_all_access_features(*args)

    @parameterized.expand(project_filter_provider())
    def test_project_filters(self, project_index, *args):
        """
        Tests the project filter
        :param project_index: Index of the project to test
        :param args: another testing features defined in _test_all_access_features method
        """
        self.apply_filter("project", self.container.all_projects[project_index])
        with self.assertLessQueries(1):
            self._test_all_access_features(*args)


del BaseTestClass
