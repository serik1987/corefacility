from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.models.enums import LevelType
from core.entity.access_level import AccessLevelSet
from core.generic_views import EntityViewMixin
from core.views.permission_viewset import PermissionViewSet
from core.os.user import PosixUser


class TestPermissionProvider(APITestCase):
    """
    Tests how permissions work on the operating system level
    """

    API_VERSION = "v1"
    LOGIN_PATH = "/api/{version}/login/".format(version=API_VERSION)
    USER_LIST_PATH = "/api/{version}/users/".format(version=API_VERSION)
    USER_DETAIL_PATH = "/api/{version}/users/%d/".format(version=API_VERSION)
    GROUP_LIST_PATH = "/api/{version}/groups/".format(version=API_VERSION)
    GROUP_DETAIL_PATH = "/api/{version}/groups/%d/".format(version=API_VERSION)
    USER_ADD_PATH = "/api/{version}/groups/%d/users/".format(version=API_VERSION)
    PROJECT_LIST_PATH = "/api/{version}/projects/".format(version=API_VERSION)
    PROJECT_DETAIL_PATH = "/api/{version}/projects/%d/".format(version=API_VERSION)
    PROJECT_PERMISSION_LIST_PATH = "/api/{version}/projects/%d/permissions/".format(version=API_VERSION)

    access_levels = None
    auth_headers = None
    user_logins = None
    group_list = None
    project_aliases = None

    @staticmethod
    def is_tests_applicable():
        return settings.CORE_MANAGE_UNIX_USERS and settings.CORE_MANAGE_UNIX_GROUPS \
               and not settings.CORE_SUGGEST_ADMINISTRATION

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        EntityViewMixin.throttle_classes = []
        PermissionViewSet.throttle_classes = []
        client = APIClient()
        cls.load_access_levels()
        cls.login(client)
        cls.create_users(client)
        cls.create_groups(client)
        cls.create_projects(client)

    @classmethod
    def tearDownClass(cls):
        client = APIClient()
        cls.delete_projects(client)
        cls.delete_groups(client)
        cls.delete_users(client)
        super().tearDownClass()

    def test_base(self):
        """
        The base test for proper permissions
        """
        for project_alias, project_id in self.project_aliases.items():
            project_result = self.client.get(self.PROJECT_PERMISSION_LIST_PATH % project_id, **self.auth_headers)
            self.assertEquals(project_result.status_code, status.HTTP_200_OK,
                              "Unable to retrieve permission list for the project " + project_alias)
            access_level_info = None
            for project_info, access_level_info in self.project_provider():
                if project_info['alias'] == project_alias:
                    break
            for group_index, access_level_alias in access_level_info.items():
                group_id = self.group_list[group_index]
                level_alias = None
                for level_info in project_result.data:
                    if level_info['group_id'] == group_id:
                        level_alias = level_info['access_level_alias']
                        break
                self.assertIsNotNone(level_alias, "The project permission was not presented in the list")
                self.assertEquals(level_alias, access_level_alias, "Unexpected access level alias")

    def test_operating_system_level_permissions(self):
        """
        Tests whether permissions were set at the operating system level
        """
        all_users_found = set()
        for user in PosixUser.iterate():
            if user.login in self.user_logins.keys():
                all_users_found.add(user.login)
        self.assertEquals(len(all_users_found), len(self.user_logins),
                          "Some tested users were not saved at the level of the operating system")

    @classmethod
    def load_access_levels(cls):
        """
        Loads the access level list
        :return: nothing
        """
        level_set = AccessLevelSet()
        level_set.type = LevelType.project_level
        cls.access_levels = dict()
        for level in level_set:
            cls.access_levels[level.alias] = level.id

    @classmethod
    def login(cls, client):
        result = client.post(cls.LOGIN_PATH)
        assert result.status_code == status.HTTP_200_OK
        token = result.data['token']
        cls.auth_headers = {"HTTP_AUTHORIZATION": "Token " + token}

    @classmethod
    def create_users(cls, client):
        """
        Creates all necessary users
        :param client: the API client
        :return: nothing
        """
        cls.user_logins = dict()
        for user_data in cls.user_provider():
            result = client.post(cls.USER_LIST_PATH, user_data, format="json", **cls.auth_headers)
            assert result.status_code == status.HTTP_201_CREATED
            cls.user_logins[result.data['login']] = result.data['id']

    @classmethod
    def delete_users(cls, client):
        """
        Deletes all users
        :param client: the API client
        :return: nothing
        """
        for _, user_id in cls.user_logins.items():
            result = client.delete(cls.USER_DETAIL_PATH % user_id, **cls.auth_headers)
            assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def create_groups(cls, client):
        """
        Creates all necessary groups and establish connections among them
        :param client: the API client
        :return: nothing
        """
        cls.group_list = []
        for group_data, user_list in cls.group_provider():
            if isinstance(group_data['governor_id'], str):
                group_data['governor_id'] = cls.user_logins[group_data['governor_id']]
            group_create_result = client.post(cls.GROUP_LIST_PATH, group_data, format="json", **cls.auth_headers)
            assert group_create_result.status_code == status.HTTP_201_CREATED
            group_id = group_create_result.data['id']
            cls.group_list.append(group_id)
            for user_login in user_list:
                user_id = cls.user_logins[user_login]
                result = client.post(cls.USER_ADD_PATH % group_id, {"user_id": user_id},
                                     format="json", **cls.auth_headers)
                assert result.status_code == status.HTTP_200_OK

    @classmethod
    def delete_groups(cls, client):
        """
        Deletes all groups that were previously created
        :param client: the API client
        :return: nothing
        """
        for group_id in cls.group_list:
            result = client.delete(cls.GROUP_DETAIL_PATH % group_id, **cls.auth_headers)
            assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def create_projects(cls, client):
        """
        Creates new project
        :param client: the API client
        :return: nothing
        """
        cls.project_aliases = dict()
        for project_data, permission_list in cls.project_provider():
            project_data['root_group_id'] = cls.group_list[project_data['root_group_id']]
            create_result = client.post(cls.PROJECT_LIST_PATH, project_data,
                                        format="json", **cls.auth_headers)
            assert create_result.status_code == status.HTTP_201_CREATED
            project_id = create_result.data['id']
            cls.project_aliases[create_result.data['alias']] = project_id
            for group_index, access_level in permission_list.items():
                permission_data = {
                    "group_id": cls.group_list[group_index],
                    "access_level_id": cls.access_levels[access_level]
                }
                result = client.post(cls.PROJECT_PERMISSION_LIST_PATH % project_id, permission_data,
                                     format="json", **cls.auth_headers)
                assert result.status_code == status.HTTP_200_OK

    @classmethod
    def delete_projects(cls, client):
        """
        Deletes the project
        :param client: the API client
        :return: nothing
        """
        for _, project_id in cls.project_aliases.items():
            result = client.delete(cls.PROJECT_DETAIL_PATH % project_id, **cls.auth_headers)
            assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def user_provider(cls):
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
                "surname": "Орехова",
            },
            {
                "login": "ilja_pavlov",
                "name": "Илья",
                "surname": "Павлов",
            },
            {
                "login": "leon_tsvetkov",
                "name": "Леон",
                "surname": "Цветков",
            },
            {
                "login": "daria_solovieva",
                "name": "Дарья",
                "surname": "Соловьева",
            },
            {
                "login": "artem_komarov",
                "name": "Артём",
                "surname": "Комаров",
            },
            {
                "login": "ilja_dmitriev",
                "name": "Илья",
                "surname": "Дмитриев",
            },
            {
                "login": "anastasia_spiridonova",
                "name": "Анастасия",
                "surname": "Спиридонова",
            },
            {
                "login": "alexander_sytchov",
                "name": "Александр",
                "surname": "Сычёв"
            }
        ]

    @classmethod
    def group_provider(cls):
        return [
            ({
                "name": "Сёстры Райт",
                "governor_id": "polina_zolotova",
            }, ["ekaterina_mironova", "maria_orekhova", "daria_solovieva"]),
            ({
                "name": "Своеобразные",
                "governor_id": "ilja_pavlov",
            }, ["ekaterina_mironova", "maria_orekhova", "leon_tsvetkov"]),
            ({
                "name": "Управляемый хаос",
                "governor_id": "leon_tsvetkov",
            }, ["ilja_pavlov", "daria_solovieva", "artem_komarov"]),
            ({
                "name": "Изгибно-крутильный флаттер",
                "governor_id": "ilja_dmitriev",
            }, ["daria_solovieva", "artem_komarov", "anastasia_spiridonova"]),
            ({
                "name": "Революция сознания",
                "governor_id": "ilja_dmitriev",
            }, ["artem_komarov", "anastasia_spiridonova", "alexander_sytchov"]),
        ]

    @classmethod
    def project_provider(cls):
        return [
            ({
                "alias": "hhna",
                "name": "Высшая нервная деятельность",
                "root_group_id": 0,
            }, {}),
            ({
                "alias": "cnl",
                "name": "Клеточная нейробиология обучения",
                "root_group_id": 0,
            }, {1: "data_process"}),
            ({
                "alias": "mnl",
                "name": "Математическая нейробиология обучения",
                "root_group_id": 1,
            }, {0: "data_full", 2: "data_view"}),
            ({
                "alias": "mn",
                "name": "Молекулярная нейробиология",
                "root_group_id": 1,
            }, {0: "data_add", 2: "no_access"}),
            ({
                "alias": "nsw",
                "name": "Нейробиология сна и бодрствования",
                "root_group_id": 2,
            }, {3: "data_add"}),
            ({
                "alias": "n",
                "name": "Нейроонтогенез",
                "root_group_id": 3,
            }, {2: "full"}),
            ({
                "alias": "nl",
                "name": "Нейрофизиология обучения",
                "root_group_id": 3,
            }, {4: "data_view"}),
            ({
                "alias": "gcn",
                "name": "Общая и клиническая нейрофизиология",
                "root_group_id": 4,
            }, {3: "data_process"}),
            ({
                "alias": "aphhna",
                "name": "Прикладная физиология",
                "root_group_id": 4,
            }, {}),
            ({
                "alias": "cr",
                "name": "Условные рефлексы",
                "root_group_id": 4,
            }, {})
        ]
