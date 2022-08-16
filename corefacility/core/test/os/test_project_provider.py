import subprocess
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from parameterized import parameterized

from core.os.group import PosixGroup, OperatingSystemGroupNotFound
from core.entity.entity_providers.posix_providers.project_provider import ProjectProvider
from core.test.views.field_test.data_providers import slug_provider


def base_project_provider():
    return {
        "alias": "hhna",
        "name": "Высшая нервная деятельность",
        "root_group_id": None
    }


def input_data_provider():
    return [
        ({
            "alias": alias,
            "name": "Высшая нервная деятельность",
            "root_group_id": None
        },)
        for alias, is_valid in slug_provider(64) if is_valid
    ]


def change_login_provider():
    return [(alias,) for alias, is_valid in slug_provider(64) if is_valid]


class TestProjectProvider(APITestCase):
    """
    Test routines for the ProjectProvider based on interaction with the operating system
    """

    API_VERSION = "v1"
    LOGIN_REQUEST_PATH = "/api/{version}/login/".format(version=API_VERSION)
    USER_LIST_PATH = "/api/{version}/users/".format(version=API_VERSION)
    USER_DETAIL_PATH = "/api/{version}/users/%d/".format(version=API_VERSION)
    GROUP_LIST_PATH = "/api/{version}/groups/".format(version=API_VERSION)
    GROUP_DETAIL_PATH = "/api/{version}/groups/%d/".format(version=API_VERSION)
    PROJECT_LIST_PATH = "/api/{version}/projects/".format(version=API_VERSION)
    PROJECT_DETAIL_PATH = "/api/{version}/projects/%d/".format(version=API_VERSION)

    auth_headers = None
    user_logins = None
    group_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        if settings.CORE_MANAGE_UNIX_GROUPS and not settings.CORE_SUGGEST_ADMINISTRATION:
            client = APIClient()
            cls.login(client)
            cls.create_users(client)
            cls.create_group(client)

    def setUp(self):
        super().setUp()
        if not settings.CORE_MANAGE_UNIX_GROUPS or settings.CORE_SUGGEST_ADMINISTRATION:
            self.skipTest("This test is written for full server configuration only")

    @classmethod
    def tearDownClass(cls):
        if settings.CORE_MANAGE_UNIX_GROUPS and not settings.CORE_SUGGEST_ADMINISTRATION:
            client = APIClient()
            cls.delete_group(client)
            cls.delete_users(client)
            super().tearDownClass()

    @parameterized.expand(input_data_provider())
    def test_create_project(self, project_arguments):
        """
        Tests whether POSIX group creates together with project creating
        """
        project_arguments['root_group_id'] = self.group_id
        project_data = self._create_project(project_arguments)
        group_name = project_data['unix_group']
        self.assertIsNotNone(group_name, "The unix_group field must be present in the output result")
        PosixGroup.find_by_name(group_name)
        self._delete_project(project_data['id'])
        with self.assertRaises(OperatingSystemGroupNotFound,
            msg="The POSIX group has not been deleted when the project has been deleted"):
            PosixGroup.find_by_name(group_name)

    @parameterized.expand(input_data_provider())
    def test_precreate_project(self, project_arguments):
        """
        Tests whether the project can be successfully created even after POSIX group is created
        """
        project_arguments['root_group_id'] = self.group_id
        unix_group = ProjectProvider._get_posix_group_name(project_arguments['alias'])
        subprocess.run(("groupadd", unix_group))
        project_data = self._create_project(project_arguments)
        group_name = project_data['unix_group']
        PosixGroup.find_by_name(group_name)
        self._delete_project(project_data['id'])

    @parameterized.expand(change_login_provider())
    def test_update_project(self, new_login):
        project_arguments = base_project_provider()
        project_arguments['root_group_id'] = self.group_id
        project_data = self._create_project(project_arguments)
        new_project_data = self._update_project(project_data['id'], new_login)
        group_name = new_project_data['unix_group']
        PosixGroup.find_by_name(group_name)
        self._delete_project(project_data['id'])

    @parameterized.expand(change_login_provider())
    def test_recreate_group(self, new_login):
        project_arguments = base_project_provider()
        project_arguments['root_group_id'] = self.group_id
        project_data = self._create_project(project_arguments)
        group_name = project_data['unix_group']
        subprocess.run(("groupdel", group_name))
        new_project_data = self._update_project(project_data['id'], new_login)
        group_name = new_project_data['unix_group']
        PosixGroup.find_by_name(group_name)
        self._delete_project(project_data['id'])

    @classmethod
    def login(cls, client):
        login_result = client.post(cls.LOGIN_REQUEST_PATH)
        token = login_result.data['token']
        cls.auth_headers = {"HTTP_AUTHORIZATION": "Token " + token}

    @classmethod
    def create_users(cls, client):
        cls.user_logins = {}
        for user_info in cls.users_provider():
            result = client.post(cls.USER_LIST_PATH, user_info, format="json", **cls.auth_headers)
            assert result.status_code == status.HTTP_201_CREATED
            cls.user_logins[result.data['login']] = result.data['id']

    @classmethod
    def create_group(cls, client):
        result = client.post(cls.GROUP_LIST_PATH, cls.group_provider(), format="json", **cls.auth_headers)
        assert result.status_code == status.HTTP_201_CREATED
        cls.group_id = result.data['id']

    @classmethod
    def delete_users(cls, client):
        for login, user_id in cls.user_logins.items():
            result = client.delete(cls.USER_DETAIL_PATH % user_id, **cls.auth_headers)
            assert result.status_code == status.HTTP_204_NO_CONTENT
        cls.user_logins = None

    @classmethod
    def delete_group(cls, client):
        result = client.delete(cls.GROUP_DETAIL_PATH % cls.group_id, **cls.auth_headers)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def users_provider(cls):
        return [
            {
                "login": "ekaterina_mironova",
                "name": "Екатерина",
                "surname": "Миронова",
            },
            {
                "login": "polina_zolotova",
                "name": "Полина",
                "surname": "Золотова",
            },
            {
                "login": "maria_orekhova",
                "name": "Мария",
                "surname": "Орехова"
            },
            {
                "login": "daria_solovieva",
                "name": "Дарья",
                "surname": "Соловьёва",
            }
        ]
    @classmethod
    def group_provider(cls):
        return {
            "name": "Сёстры Райт",
            "governor_id": cls.user_logins['polina_zolotova']
        }

    def _create_project(self, project_data):
        result = self.client.post(self.PROJECT_LIST_PATH, project_data, format="json", **self.auth_headers)
        self.assertEquals(result.status_code, status.HTTP_201_CREATED,
            "Unexpected status code during the project create")
        return result.data

    def _update_project(self, project_id, new_login):
        result = self.client.patch(self.PROJECT_DETAIL_PATH % project_id, data={"alias": new_login},
            format="json", **self.auth_headers)
        self.assertEquals(result.status_code, status.HTTP_200_OK, "Unexpected status code during the project update")
        return result.data

    def _delete_project(self, project_id):
        result = self.client.delete(self.PROJECT_DETAIL_PATH % project_id, **self.auth_headers)
        self.assertEquals(result.status_code, status.HTTP_204_NO_CONTENT,
            "Unexpected status code during the project delete")
