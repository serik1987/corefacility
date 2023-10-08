import os

from django.conf import settings
from .base_test_class import TestFileSystem


class TestUserProvider(TestFileSystem):
    """
    Test routines for the user provider
    """

    API_VERSION = "v1"
    ENTITY_LIST_PATH = "/api/{version}/users/".format(version=API_VERSION)
    ENTITY_DETAIL_PATH = "/api/{version}/users/%d/".format(version=API_VERSION)

    ENTITY_CREATE_DATA = {"login": "ordinary_user"}
    ENTITY_UPDATE_DATA = {"login": "another_user"}

    TEST_FILENAME = "test_file.txt"
    TEST_FILE_DATA = "Hello, World!"

    @classmethod
    def is_test_applicable(cls):
        return not settings.CORE_MANAGE_UNIX_USERS

    def assert_entity_dir_created(self, user_data):
        """
        Asserts that the home directory for the user has been created
        :param user_data: the user data returned by the create_entity function
        :return: nothing
        """
        home_dir = user_data['home_dir']
        self.assertIsNotNone(home_dir, "The user's home directory was not present in the output")
        self.assertTrue(os.path.isdir(home_dir), "The user's home directory is expected to be exist")

    def create_test_file(self, entity_data):
        """
        Creates test file in the entity directory
        :param entity_data: the entity data returned by the create_entity function
        :return: nothing
        """
        test_filename = os.path.join(entity_data['home_dir'], self.TEST_FILENAME)
        with open(test_filename, "w") as test_file:
            test_file.write(self.TEST_FILE_DATA)

    def assert_test_file_exists(self, entity_data):
        """
        Asserts that the test file still exists in the entity directory
        :param entity_data: the entity data returned during the last create/update request
        :return: nothing
        """
        test_filename = os.path.join(entity_data['home_dir'], self.TEST_FILENAME)
        self.assertTrue(os.path.isfile(test_filename), "The test file was lost during the entity update")
        with open(test_filename, "r") as test_file:
            file_data = test_file.read()
        self.assertEquals(file_data, self.TEST_FILE_DATA, "The test file content was lost during the entity update")

    def assert_entity_dir_deleted(self, entity_data):
        """
        Asserts that the home directory for the entity has been deleted
        :param entity_data: the entity data returned by the delete_entity function
        :return: nothing
        """
        self.assertFalse(os.path.isdir(entity_data['home_dir']),
                         "The user's home directory still exists even after its delete")


del TestFileSystem
