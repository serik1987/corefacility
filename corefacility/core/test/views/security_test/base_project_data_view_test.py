from rest_framework import status
from parameterized import parameterized

from django.conf import settings

from core.models.enums import LevelType
from core.entity.user import User
from core.entity.group import Group
from core.entity.project import Project
from core.entity.access_level import AccessLevelSet
from core.entity.entity_providers.posix_providers.posix_provider import PosixProvider
from core.entity.entity_providers.file_providers.files_provider import FilesProvider
from core.entity.entry_points.authorizations import AuthorizationModule

from .base_test_class import BaseTestClass


class BaseProjectDataViewTest(BaseTestClass):
    """
    Base class for testing all project-related views
    """

    superuser_required = False
    ordinary_user_required = False

    access_levels = None
    """ A dictionary where all keys are access level aliases and values are their corresponding access level objects """

    user_list = None
    """ A dictionary where all keys are user logins and values are their corresponding user objects """

    group_list = None
    """ A dictionary where all keys are governor logins and values are their corresponding group objects """

    project = None
    """ The testing project """

    @classmethod
    def setUpTestData(cls):
        """
        This method executes before all tests in the class and shall be used to create proper test environment
        for them
        """
        super().setUpTestData()
        if not settings.CORE_SUGGEST_ADMINISTRATION:
            PosixProvider.force_disable = False
            FilesProvider.force_disable = False
        cls.load_access_levels()
        cls.create_users_and_groups()
        cls.create_project()

    @classmethod
    def tearDownClass(cls):
        """
        This method executes after all tests in the class and shall restore previous system state
        """
        if cls.project is not None:
            cls.project.delete()
        cls.delete_users_and_groups()
        super().tearDownClass()

    @classmethod
    def load_access_levels(cls):
        """
        Loads all project access levels from the database
        """
        cls.access_levels = dict()
        level_set = AccessLevelSet()
        level_set.type = LevelType.project_level
        for access_level in AccessLevelSet():
            cls.access_levels[access_level.alias] = access_level

    @classmethod
    def create_users_and_groups(cls):
        """
        Adds users and groups to your test environment. This function also creates proper user tokens
        """
        cls.user_list = dict()
        cls.group_list = dict()
        for login, name, surname in cls.get_users_info():
            user = User(login=login, name=name, surname=surname)
            if login == "superuser":
                user.is_superuser = True
            user.create()
            cls.user_list[user.login] = user
            group = Group(name="Personal group for %s %s" % (name, surname), governor=user)
            group.create()
            cls.group_list[user.login] = group
            token = AuthorizationModule.issue_token(user)
            setattr(cls, login + "_token", token)

    @classmethod
    def delete_users_and_groups(cls):
        """
        Removes all users and groups from the test environment.
        """
        for login, user in cls.user_list.items():
            cls.group_list[login].delete()
            user.delete()

    @classmethod
    def create_project(cls):
        """
        Creates the test projects and sets its proper permissions
        """
        cls.project = Project(alias="test_project", name="The Test Project", root_group=cls.group_list['full'])
        cls.project.create()
        for login, group in cls.group_list.items():
            if login not in ("superuser", "full", "ordinary_user"):
                cls.project.permissions.set(group, cls.access_levels[login])

    @classmethod
    def get_users_info(cls):
        """
        Returns the info for all users that shall be created for the sake of the test environment
        :return:  List of (login_and_access_level, name, surname) tuple
        """
        return [
            ("superuser", "Administrator", "Superuserov"),
            ("full", "Full", "Accessov"),
            ("data_full", "Data", "Fullov"),
            ("data_add", "Data", "Addov"),
            ("data_process", "Data", "Processov"),
            ("data_view", "Data", "Viewerov"),
            ("no_access", "Pinky", "Unaccessor"),
            ("ordinary_user", "Pinky", "Loser"),
        ]

    @parameterized.expand([
        ("default", "superuser", status.HTTP_201_CREATED),
        ("default", "full", status.HTTP_201_CREATED),
        ("default", "data_full", status.HTTP_201_CREATED),
        ("default", "data_add", status.HTTP_201_CREATED),
        ("default", "data_process", "data_process"),
        ("default", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_create(self, test_data_id, token_id, expected_status_code):
        """
        Tests creating action for entity views
        :param test_data_id: The test data contains in the public field "{id}_data" where {id} is test_data_id
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param expected_status_code: a status code that shall be checked. If status code is between 200 and 299
            an additional check for the response body is provided
        :return: nothing
        :except: assertion error if status code is not the same as expected_status_code or test data were either
            not saved correctly or not contained in the response body
        """
        if isinstance(expected_status_code, str):
            expected_status_code = getattr(self, expected_status_code + "_status")
        self._test_entity_create(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("default", "superuser", status.HTTP_200_OK),
        ("default", "full", status.HTTP_200_OK),
        ("default", "data_full", status.HTTP_200_OK),
        ("default", "data_add", status.HTTP_200_OK),
        ("default", "data_process", status.HTTP_200_OK),
        ("default", "data_view", status.HTTP_200_OK),
        ("default", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_get(self, test_data_id, token_id, expected_status_code):
        """
        Testing the get action for entity views.
        :param test_data_id: The test data contains in the public field "{id}_data" where {id} is test_data_id
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param expected_status_code: a status code that shall be checked. If status code is between 200 and 299
            an additional check for the response body is provided
        :return: nothing
        :except: assertion error if status code is not the same as expected_status_code or test data were either
            not saved correctly or not contained in the response body
        """
        if isinstance(expected_status_code, str):
            expected_status_code = getattr(self, expected_status_code + "_status")
        self._test_entity_get(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("default", "updated", "superuser", status.HTTP_200_OK),
        ("default", "updated", "full", status.HTTP_200_OK),
        ("default", "updated", "data_full", status.HTTP_200_OK),
        ("default", "updated", "data_add", status.HTTP_200_OK),
        ("default", "updated", "data_process", "data_process"),
        ("default", "updated", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "updated", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "updated", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", "updated", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_update(self, test_data_id, updated_data_id, token_id, expected_response_code):
        """
        Testing the update action for views.

        The data ID is a part of a public class field containing the data. To take the data this function
        will append the "_data" suffix to the data ID and will refer to the public field with a given name.

        The token ID is a part of a public class field containing the token. To take the token this function
        will append the "_token" suffix to the data ID and will refer to the public field with a given name
        :param test_data_id: ID for the initial data
        :param updated_data_id: ID for the data patch. PUTting the updated_data shall result in error 400 but
            PUTting the test_data + updated_data shall result in success
        :param token_id: token corresponding to the authorized user
        :param expected_response_code: the response code that you expect
        :return: nothing
        """
        if isinstance(expected_response_code, str):
            expected_response_code = getattr(self, expected_response_code + "_status")
        self._test_entity_update(test_data_id, updated_data_id, token_id, expected_response_code)

    @parameterized.expand([
        ("default", "updated", "superuser", status.HTTP_200_OK),
        ("default", "updated", "full", status.HTTP_200_OK),
        ("default", "updated", "data_full", status.HTTP_200_OK),
        ("default", "updated", "data_add", status.HTTP_200_OK),
        ("default", "updated", "data_process", "data_process"),
        ("default", "updated", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "updated", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "updated", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", "updated", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_partial_update(self, test_data_id, updated_data_id, token_id, expected_response_code):
        """
        Testing the partial updating action for views.

        Testing the update action for views.

        The data ID is a part of a public class field containing the data. To take the data this function
        will append the "_data" suffix to the data ID and will refer to the public field with a given name.

        The token ID is a part of a public class field containing the token. To take the token this function
        will append the "_token" suffix to the data ID and will refer to the public field with a given name.

        :param test_data_id: ID for the initial data
        :param updated_data_id: ID for the data patch. PUTting the updated_data shall result in error 400 but
            PUTting the test_data + updated_data shall result in success.
        :param token_id: token corresponding to the authorized user.
        :param expected_response_code: the response code that you expect.
        :return: nothing
        """
        if isinstance(expected_response_code, str):
            expected_response_code = getattr(self, expected_response_code + "_status")
        self._test_entity_partial_update(test_data_id, updated_data_id, token_id, expected_response_code)

    @parameterized.expand([
        ("default", "superuser", status.HTTP_204_NO_CONTENT),
        ("default", "full", status.HTTP_204_NO_CONTENT),
        ("default", "data_full", status.HTTP_204_NO_CONTENT),
        ("default", "data_add", status.HTTP_403_FORBIDDEN),
        ("default", "data_process", status.HTTP_403_FORBIDDEN),
        ("default", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def _test_entity_destroy(self, test_data_id, token_id, expected_status_code):
        """
        Tests the destroy action for views.

        :param test_data_id: The test data contains in the public field "{id}_data" where {id} is test_data_id
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param expected_status_code: a status code that shall be checked. If status code is between 200 and 299
            an additional check for the response body is provided
        :return: nothing
        :except: assertion error if status code is not the same as expected_status_code or test data were either
            not saved correctly or not contained in the response body
        """


del BaseTestClass
