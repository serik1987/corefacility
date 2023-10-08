import os

from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from .base_test_class import TestFileSystem


class TestProjectProvider(TestFileSystem):
    """
    Provides testing routines for the ProjectFilesProvider
    """

    API_VERSION = "v1"
    """ Defines a testing API version """

    ENTITY_LIST_PATH = "/api/{version}/projects/".format(version=API_VERSION)
    """ Path for downloading the entity list or creating new entity """

    ENTITY_DETAIL_PATH = "/api/{version}/projects/%d/".format(version=API_VERSION)
    """ Path for entity read, modify or delete operations, Use %d placeholder to mark the entity ID """

    ENTITY_CREATE_DATA = {
        "alias": "vasomotor-oscillations",
        "name": "Вазомоторные колебания",
        "root_group_id": None,
    }
    """ Data to be used for the entity create """

    ENTITY_UPDATE_DATA = {"alias": "vmo"}
    """ Data to be used for the entity update """

    USER_LIST_PATH = "/api/{version}/users/".format(version=API_VERSION)
    USER_DETAIL_PATH = "/api/{version}/users/%d/".format(version=API_VERSION)
    USER_DATA = {"login": "sergei_kozhukhov"}

    GROUP_LIST_PATH = "/api/{version}/groups/".format(version=API_VERSION)
    GROUP_DETAIL_PATH = "/api/{version}/groups/%d/".format(version=API_VERSION)
    GROUP_DATA = {"name": "Основная группа", "governor_id": None}

    user_id = None
    """ ID for the root group governor """

    group_id = None
    """ ID for the root group """

    TEST_FILENAME = "test.txt"
    TEST_FILE_CONTENT = "Hello, World!"

    @classmethod
    def is_test_applicable(cls):
        """
        Defines conditions where all tests shall be run under
        :return: True if all tests shall be run, False if they shall be skipped
        """
        return not settings.CORE_MANAGE_UNIX_GROUPS

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        if cls.is_test_applicable():
            client = APIClient()
            cls._create_user(client)
            cls._create_group(client)

    @classmethod
    def tearDownClass(cls):
        if cls.is_test_applicable():
            client = APIClient()
            cls._destroy_group(client)
            cls._destroy_user(client)
        super().tearDownClass()

    @classmethod
    def _create_user(cls, client):
        """
        Creates the root group governor for all projects
        :param client: the API client that shall be used to create a single user
        :return: nothing
        """
        response = client.post(cls.USER_LIST_PATH, cls.USER_DATA, format="json", **cls.auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        cls.user_id = response.data['id']

    @classmethod
    def _destroy_user(cls, client):
        """
        Destroys the root group governor for all projects
        :param client: the API client that shall be used to destroy the user
        :return: nothing
        """
        response = client.delete(cls.USER_DETAIL_PATH % cls.user_id, **cls.auth_headers)
        if response.status_code != status.HTTP_204_NO_CONTENT:
            print(response, response.data)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        cls.user_id = None

    @classmethod
    def _create_group(cls, client):
        """
        Creates the project's root group
        :param client: the API client that shall be used to create the group
        :return: nothing
        """
        group_data = cls.GROUP_DATA.copy()
        group_data['governor_id'] = cls.user_id
        response = client.post(cls.GROUP_LIST_PATH, group_data, format="json", **cls.auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        cls.group_id = response.data['id']

    @classmethod
    def _destroy_group(cls, client):
        """
        Destroys the project's root group
        :param client: the API client that shall be used to destroy the group
        :return: nothing
        """
        response = client.delete(cls.GROUP_DETAIL_PATH % cls.group_id, **cls.auth_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        cls.group_id = None

    @property
    def entity_create_data(self):
        """
        Data that will be used for the entity create
        """
        data = super().entity_create_data.copy()
        data['root_group_id'] = self.group_id
        return data

    def assert_entity_dir_created(self, project_data):
        """
        Asserts that the project directory has already been created
        :param project_data: the project data returned by the project create or update request
        :return: nothing
        """
        project_dir = project_data['project_dir']
        self.assertIsNotNone(project_dir, "The project's 'project_dir' field shall be filled by the relevant "
                                          "project directory")
        self.assertTrue(os.path.isdir(project_dir), "The project directory must be created")

    def assert_entity_dir_deleted(self, entity_data):
        """
        Asserts that the home directory for the entity has been deleted
        :param entity_data: the entity data returned by the delete_entity function
        :return: nothing
        """
        self.assertFalse(os.path.isdir(entity_data['project_dir']),
                         "The project's directory has not been deleted together with the project delete")

    def create_test_file(self, entity_data):
        """
        Creates test file in the entity directory
        :param entity_data: the entity data returned by the create_entity function
        :return: nothing
        """
        test_filename = os.path.join(entity_data['project_dir'], self.TEST_FILENAME)
        with open(test_filename, "w") as test_file:
            test_file.write(self.TEST_FILE_CONTENT)

    def assert_test_file_exists(self, entity_data):
        """
        Asserts that the test file still exists in the entity directory
        :param entity_data: the entity data returned during the last create/update request
        :return: nothing
        """
        test_filename = os.path.join(entity_data['project_dir'], self.TEST_FILENAME)
        with open(test_filename, "r") as test_file:
            content = test_file.read()
        self.assertEquals(content, self.TEST_FILE_CONTENT,
                          "Content of the test file was not saved during the project alias change")


del TestFileSystem
