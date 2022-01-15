import warnings

from parameterized import parameterized

from core.tests.data_providers.field_value_providers import image_provider
from .base_test_class import BaseTestClass
from .entity_set_objects.user_set_object import UserSetObject
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.project_set_object import ProjectSetObject


def general_data_provider():
    return [
        (BaseTestClass.TEST_FIND_BY_ID, 3, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, 8, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ID, -1, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_ALIAS, "cnl", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "mn", BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_ALIAS, "xz", BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_FIND_BY_INDEX, 0, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 3, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 9, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, -1, BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_FIND_BY_INDEX, 10, BaseTestClass.NEGATIVE_TEST_CASE),

        (BaseTestClass.TEST_SLICING, (3, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (0, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (-1, 7, 1), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (5, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (6, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (7, 7, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 3, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 4, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 10, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 11, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (8, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (9, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (10, 20, 1), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 7, 2), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 7, 0), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, 7, None), BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (3, None, None), BaseTestClass.NEGATIVE_TEST_CASE),
        (BaseTestClass.TEST_SLICING, (None, None, None), BaseTestClass.POSITIVE_TEST_CASE),

        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def search_filter_provider():
    return [
        (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


def name_search_provider():
    return [
        ("Нейроонтогенез", BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейроонтогенез", BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_ID, 0, BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_ID, 2, BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_ID, None, BaseTestClass.NEGATIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_ALIAS, "n", BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_ALIAS, "nl", BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_ALIAS, "mnl", BaseTestClass.NEGATIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_INDEX, 2, BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_FIND_BY_INDEX, 3, BaseTestClass.NEGATIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_SLICING, (0, 10, 1), BaseTestClass.POSITIVE_TEST_CASE),
        ("Нейро", BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ("", BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        (None, BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
        ("Название несуществующего проекта", BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
    ]


class TestProjectSet(BaseTestClass):
    """
    Tests the project set
    """

    IMAGE_PROVIDER_TEST_NUMBER_INDEX = 2

    _user_set_object = None
    _group_set_object = None
    __project_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls.__project_set_object = ProjectSetObject(cls._group_set_object)
        test_avatar_files = [image_info for image_info in image_provider()
                             if image_info[cls.IMAGE_PROVIDER_TEST_NUMBER_INDEX] == 0]
        cls.load_random_avatars(cls.__project_set_object, (0, 3, 7), "avatar", test_avatar_files)

    def setUp(self):
        super().setUp()
        self.__user_set_object = TestProjectSet._user_set_object
        self.__group_set_object = TestProjectSet._group_set_object
        self._container = self.__project_set_object.clone()
        self._container.sort()
        self.initialize_filters()

    @parameterized.expand(general_data_provider())
    def test_no_filters(self, test_number, arg, test_type):
        with self.assertLessQueries(1):
            self._test_all_access_features(test_number, arg, test_type)

    @parameterized.expand(name_search_provider())
    def test_name_filter(self, project_name, test_number, arg, test_type):
        self.apply_filter("name", project_name)
        with self.assertLessQueries(1):
            self._test_all_access_features(test_number, arg, test_type)

    def test_name_filter_invalid(self):
        self.apply_filter("name", 42)
        with self.assertRaises(ValueError, msg="Incorrect value was set to the project name filter"):
            self.get_entity_set()

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        """
        Asserts that the entity has been successfully found.
        Class derivatives can re-implement this method to ensure that all entity fields were uploaded successfully.

        :param actual_entity: the entity found in the database
        :param expected_entity: the entity expected to be found in the database
        :param msg: message to print when the entity is failed to be found
        :return: nothing
        """
        super().assertEntityFound(actual_entity, expected_entity, msg)
        self.assertEquals(actual_entity.alias, expected_entity.alias,
                          "%s. The entity alias is not the same as expected" % msg)
        self.assertEquals(actual_entity.avatar.url, expected_entity.avatar.url,
                          "%s. URLs for the entity avatars are not the same as expected" % msg)
        self.assertEquals(actual_entity.name, expected_entity.name,
                          "%s. Project name is not the same as expected" % msg)
        self.assertEquals(actual_entity.description, expected_entity.description,
                          "%s. Project description is not the same as expected" % msg)
        self.assertEquals(actual_entity.governor, expected_entity.governor,
                          "%s. Project governor is not the same as expected" % msg)
        self.assertEquals(actual_entity.root_group, expected_entity.root_group,
                          "%s. Project root group is not the same as expected" % msg)
        self.assertEquals(actual_entity.project_dir, expected_entity.project_dir,
                          "%s. Project root directory is not the same as expected" % msg)
        self.assertEquals(actual_entity.unix_group, expected_entity.unix_group,
                          "%s. UNIX group is not the same as expected" % msg)


del BaseTestClass
