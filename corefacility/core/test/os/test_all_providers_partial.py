import subprocess
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from core.entity.user import UserSet
from core.entity.group import GroupSet
from core.entity.project import ProjectSet
from core.generic_views import EntityViewMixin
from core.views.permission_viewset import PermissionViewSet


class TestAllProvidersPartial(APITestCase):
    """
    Testing user provider, project provider and permission provider (for partial server configuration only)
    """

    API_VERSION = "v1"
    LOGIN_PATH = "/api/{version}/login/".format(version=API_VERSION)
    ACCESS_LEVEL_LIST_PATH = "/api/{version}/access-levels/".format(version=API_VERSION)
    USER_LIST_PATH = "/api/{version}/users/".format(version=API_VERSION)
    USER_DETAIL_PATH = "/api/{version}/users/%d/".format(version=API_VERSION)
    GROUP_LIST_PATH = "/api/{version}/groups/".format(version=API_VERSION)
    USER_ADD_PATH = "/api/{version}/groups/%d/users/".format(version=API_VERSION)
    USER_REMOVE_PATH = "/api/{version}/groups/%d/users/%d/".format(version=API_VERSION)
    GROUP_DETAIL_PATH = "/api/{version}/groups/%d/".format(version=API_VERSION)
    PROJECT_LIST_PATH = "/api/{version}/projects/".format(version=API_VERSION)
    PROJECT_DETAIL_PATH = "/api/{version}/projects/%d/".format(version=API_VERSION)
    PERMISSION_LIST_PATH = "/api/{version}/projects/%d/permissions/".format(version=API_VERSION)
    PERMISSION_DETAIL_PATH = "/api/{version}/projects/%d/permissions/%d/".format(version=API_VERSION)

    auth_headers = None
    """ Authorization headers to be placed to each HTTP request """

    access_level_ids = None
    """ A dictionary which keys are access level aliases and values are their corresponding IDs """

    user_ids = None
    """ A dictionary which keys are user logins and which values are their corresponding IDs """

    group_ids = None
    """ List of IDs of all groups in order where they are created """

    project_ids = None
    """ A dictionary which keys are project aliases and values are their corresponding IDs """

    @staticmethod
    def is_test_applicable():
        return settings.CORE_SUGGEST_ADMINISTRATION and settings.CORE_MANAGE_UNIX_USERS and \
            settings.CORE_MANAGE_UNIX_GROUPS

    @classmethod
    def login(cls, client):
        """
        Performs the authentication via 'support' user
        :param client: the HTTP client
        :return: nothing
        """
        result = client.post(cls.LOGIN_PATH)
        assert result.status_code == status.HTTP_200_OK
        token = result.data['token']
        cls.auth_headers = {"HTTP_AUTHORIZATION": "Token " + token}

    @classmethod
    def create_user(cls, client, login, name, surname):
        """
        Creates a single user
        :param client: the API client
        :param login: user's login
        :param name: user's name
        :param surname: user's surname
        :return: nothing
        """
        posix_result = subprocess.run(("useradd",
            "-c", "%s %s,,," % (name, surname),
            "-d", "/home/%s" % login,
            "-U", "-s", "/bin/bash",
            login))
        user_data = {"login": login, "name": name, "surname": surname}
        result = client.post(cls.USER_LIST_PATH, user_data, format="json", **cls.auth_headers)
        if result.status_code != status.HTTP_201_CREATED:
            print(result.status_code, result.data)
        assert result.status_code == status.HTTP_201_CREATED
        user_id = result.data['id']
        cls.user_ids[login] = user_id

    @classmethod
    def change_user_surname(cls, api_client, login, new_surname, command_clue=None):
        """
        Changes surname for a single user
        :param api_client: the API client that will be used for the user's surname change
        :param login: user's login
        :param new_surname: new surname of the user
        :return: nothing
        """
        if command_clue is not None:
            subprocess.run(command_clue)
        user_id = cls.user_ids[login]
        change_surname_path = cls.USER_DETAIL_PATH % user_id
        change_surname_data = {"surname": new_surname}
        result = api_client.patch(change_surname_path, change_surname_data, format="json", **cls.auth_headers)
        if result.status_code != status.HTTP_200_OK:
            print(result, result.data)
        assert result.status_code == status.HTTP_200_OK

    @classmethod
    def change_user_login(cls, api_client, login, new_login):
        """
        Changes login for a single user
        :param api_client: the API client that will be used for the user's login change
        :param login: old user login
        :param new_login: new user login
        :return: nothing
        """
        subprocess.run(("usermod", "-m", "-d" "/home/" + new_login, "-l", new_login, login))
        subprocess.run(("groupmod", "-n", new_login, login))
        user_id = cls.user_ids[login]
        change_login_path = cls.USER_DETAIL_PATH % user_id
        change_login_data = {"login": new_login}
        change_login_result = api_client.patch(change_login_path, change_login_data, format="json", **cls.auth_headers)
        if change_login_result.status_code != status.HTTP_200_OK:
            print(change_login_result, change_login_result.data)
        assert change_login_result.status_code == status.HTTP_200_OK
        del cls.user_ids[login]
        cls.user_ids[change_login_result.data['login']] = change_login_result.data['id']

    @classmethod
    def delete_user(cls, api_client, login):
        """
        Deletes a user with a given ID
        :param api_client: the API client used for deleting
        :param login: the user ID
        :return: nothing
        """
        subprocess.run(("userdel", "-rf", login), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(("sh", "-c", "groupdel %s || echo" % login), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        delete_path = cls.USER_DETAIL_PATH % cls.user_ids[login]
        result = api_client.delete(delete_path, **cls.auth_headers)
        if result.status_code != status.HTTP_204_NO_CONTENT:
            print(result, result.data)
        assert result.status_code == status.HTTP_204_NO_CONTENT
        del cls.user_ids[login]

    @classmethod
    def create_group(cls, api_client, group_name, governor_login):
        """
        Creates a scientific group
        :param api_client: the API client that shall be used to create the group
        :param group_name: name of the group
        :param governor_login: governor's login
        :return: nothing
        """
        group_details = {"name": group_name, "governor_id": cls.user_ids[governor_login]}
        result = api_client.post(cls.GROUP_LIST_PATH, group_details, format="json", **cls.auth_headers)
        group_id = result.data['id']
        cls.group_ids.append(group_id)

    @classmethod
    def attach_user(cls, api_client, group_index, user_login, command_queue=None):
        """
        Adds the user to the group
        :param api_client: the API client that shall be used to create the group
        :param group_index: index of the group within the group list
        :param user_login: login of the user to add
        :return: nothing
        """
        if command_queue is not None:
            subprocess.run(command_queue)
        group_id = cls.group_ids[group_index]
        user_id = cls.user_ids[user_login]
        user_add_path = cls.USER_ADD_PATH % group_id
        user_add_data = {"user_id": user_id}
        result = api_client.post(user_add_path, user_add_data, format="json", **cls.auth_headers)
        if result.status_code != status.HTTP_200_OK:
            print(result, result.data)
        assert result.status_code == status.HTTP_200_OK

    @classmethod
    def detach_user(cls, api_client, group_index, user_login, command_queue=None):
        """
        Removes the user from the group
        :param api_client: the API client that shall be used for such removal
        :param group_index: index of the group within the group list
        :param user_login: login of the user to add
        :return: nothing
        """
        if command_queue is not None:
            subprocess.run(command_queue)
        group_id = cls.group_ids[group_index]
        user_id = cls.user_ids[user_login]
        user_detach_path = cls.USER_REMOVE_PATH % (group_id, user_id)
        result = api_client.delete(user_detach_path, **cls.auth_headers)
        if result.status_code != status.HTTP_204_NO_CONTENT:
            print(result, result.data)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def delete_group(cls, api_client, group_index):
        """
        Removes the scientific group
        :param api_client: the API client that shall be used to destroy the group
        :param group_index: index of the group within the group ID list
        :return: nothing
        """
        group_id = cls.group_ids[group_index]
        delete_path = cls.GROUP_DETAIL_PATH % group_id
        result = api_client.delete(delete_path, **cls.auth_headers)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def create_project(cls, api_client, alias, name, root_group_index):
        """
        Creates a project
        :param api_client: API client that shall be used to create a project
        :param alias: desired project alias
        :param name: desired project name
        :param root_group_index: desired root group index
        :return: nothing
        """
        group_id = cls.group_ids[root_group_index]
        group = GroupSet().get(group_id)
        subprocess.run(("groupadd", "-f", alias))
        for user in group.users:
            subprocess.run(("usermod", "-aG", alias, user.unix_group))
        project_data = {"alias": alias, "name": name, "root_group_id": group_id}
        result = api_client.post(cls.PROJECT_LIST_PATH, project_data, format="json", **cls.auth_headers)
        if result.status_code != status.HTTP_201_CREATED:
            print(result, result.data)
        assert result.status_code == status.HTTP_201_CREATED
        cls.project_ids[alias] = result.data['id']

    @classmethod
    def change_project_alias(cls, api_client, alias, new_alias):
        """
        Modifies the project alias
        :param api_client: API client that will be used for such a modification
        :param alias: old project alias
        :param new_alias: new project alias
        :return: nothing
        """
        subprocess.run(("groupmod", "-n", new_alias, alias))
        project_id = cls.project_ids[alias]
        alias_change_path = cls.PROJECT_DETAIL_PATH % project_id
        alias_change_data = {"alias": new_alias}
        result = api_client.patch(alias_change_path, alias_change_data, format="json", **cls.auth_headers)
        if result.status_code != status.HTTP_200_OK:
            print(result, result.data)
        assert result.status_code == status.HTTP_200_OK
        del cls.project_ids[alias]
        cls.project_ids[result.data['alias']] = result.data['id']

    @classmethod
    def delete_project(cls, api_client, alias):
        """
        Deletes a project
        :param api_client: API client that shall be used to delete a project
        :param alias: desired project alias
        :return: nothing
        """
        subprocess.run(("groupdel", alias))
        project_delete_path = cls.PROJECT_DETAIL_PATH % cls.project_ids[alias]
        result = api_client.delete(project_delete_path, **cls.auth_headers)
        if result.status_code != status.HTTP_204_NO_CONTENT:
            print(result, result.data)
        assert result.status_code == status.HTTP_204_NO_CONTENT
        del cls.project_ids[alias]

    @classmethod
    def set_permission(cls, api_client, project_alias, group_index, access_level_alias):
        """
        Sets the permission for the project
        :param api_client: API client that shall be used to set a permission
        :param project_alias: alias of a project which permission shall be set
        :param group_index: index of a group that shall be attached to the project
        :param access_level_alias: alias of the access level that gain all group members, including the group governor
        :return: nothing
        """
        group_id = cls.group_ids[group_index]
        if access_level_alias != "no_access":
            group = GroupSet().get(group_id)
            for user in group.users:
                subprocess.run(("usermod", "-aG", project_alias, user.unix_group))
        set_permission_path = cls.PERMISSION_LIST_PATH % cls.project_ids[project_alias]
        permission_data = {
            "group_id": group_id,
            "access_level_id": cls.access_level_ids[access_level_alias]
        }
        result = api_client.post(set_permission_path, permission_data, format="json", **cls.auth_headers)
        if result.status_code != status.HTTP_200_OK:
            print(result.status_code, result.data)
        assert result.status_code == status.HTTP_200_OK

    @classmethod
    def delete_permission(cls, api_client, project_alias, group_index, command_clues=None):
        """
        Deletes permission from the project
        :param api_client: API client that shall be used to delete a permission
        :param project_alias: alias of a project which permission shall be deleted
        :param group_index: index of a group that shall be detached from the project
        :return: nothing
        """
        if command_clues is not None:
            for clue in command_clues:
                subprocess.run(clue)
        project_id = cls.project_ids[project_alias]
        group_id = cls.group_ids[group_index]
        permission_delete_path = cls.PERMISSION_DETAIL_PATH % (project_id, group_id)
        result = api_client.delete(permission_delete_path, **cls.auth_headers)
        if result.status_code != status.HTTP_204_NO_CONTENT:
            print(result, result.data)
        assert result.status_code == status.HTTP_204_NO_CONTENT

    @classmethod
    def create_all_users(cls, api_client):
        """
        Creates all users in the dataset
        :param api_client: the APIClient instance that shall be used to create all users
        :return: nothing
        """
        cls.user_ids = dict()
        cls.create_user(api_client, "ekaterina_mironova", "Екатерина", "Миронова")
        cls.create_user(api_client, "polina_zolotova", "Полина", "Золотова")
        cls.create_user(api_client, "maria_orekhova", "Мария", "Орехова")
        cls.create_user(api_client, "ilja_pavlov", "Илья", "Павлов")
        cls.create_user(api_client, "leon_tsvetkov", "Леон", "Цветков")
        cls.create_user(api_client, "daria_solovieva", "Дарья", "Соловьёва")
        cls.create_user(api_client, "artem_komarov", "Артём", "Комаров")
        cls.create_user(api_client, "ilja_dmitriev", "Илья", "Дмитриев")
        cls.create_user(api_client, "anastasia_spiridonova", "Анастасия", "Спиридонова")
        cls.create_user(api_client, "alexander_sytchov", "Александр", "Сычёв")

    @classmethod
    def delete_all_users(cls, api_client):
        """
        Deletes all users from the dataset
        :param api_client: the APIClient instance that shall be used to delete all users
        :return: nothing
        """
        for user_login in list(cls.user_ids.keys()):
            cls.delete_user(api_client, user_login)

    @classmethod
    def load_access_levels(cls, api_client):
        """
        Loads all access levels
        :param api_client: the API client that will be used to load all access levels
        :return: nothing
        """
        cls.access_level_ids = dict()
        result = api_client.get(cls.ACCESS_LEVEL_LIST_PATH, {"type": "prj"}, **cls.auth_headers)
        assert result.status_code == status.HTTP_200_OK
        for access_level_info in result.data:
            cls.access_level_ids[access_level_info['alias']] = access_level_info['id']

    @classmethod
    def create_all_groups(cls, api_client):
        """
        Creates all groups within the dataset
        :param api_client: the APIClient instance that shall be used to create all groups
        :return: nothing
        """
        cls.group_ids = list()
        cls.create_group(api_client, "Сёстры Райт", "polina_zolotova")  # index 0
        cls.create_group(api_client, "Своеобразные", "ilja_pavlov")  # index 1
        cls.create_group(api_client, "Управляемый хаос", "leon_tsvetkov")  # index 2
        cls.create_group(api_client, "Изгибно-крутильный флаттер", "ilja_dmitriev")  # index 3
        cls.create_group(api_client, "Революция сознания", "ilja_dmitriev")  # index 4

        cls.attach_user(api_client, 0, "ekaterina_mironova")
        cls.attach_user(api_client, 0, "maria_orekhova")
        cls.attach_user(api_client, 0, "daria_solovieva")

        cls.attach_user(api_client, 1, "ekaterina_mironova")
        cls.attach_user(api_client, 1, "maria_orekhova")
        cls.attach_user(api_client, 1, "leon_tsvetkov")

        cls.attach_user(api_client, 2, "ilja_pavlov")
        cls.attach_user(api_client, 2, "daria_solovieva")
        cls.attach_user(api_client, 2, "artem_komarov")

        cls.attach_user(api_client, 3, "daria_solovieva")
        cls.attach_user(api_client, 3, "artem_komarov")
        cls.attach_user(api_client, 3, "anastasia_spiridonova")

        cls.attach_user(api_client, 4, "artem_komarov")
        cls.attach_user(api_client, 4, "anastasia_spiridonova")
        cls.attach_user(api_client, 4, "alexander_sytchov")

    @classmethod
    def delete_all_groups(cls, api_client):
        """
        Deletes all groups within the dataset
        :param api_client: the APIClient instance that shall be used to delete all groups
        :return: nothing
        """
        group_number = len(cls.group_ids)
        for group_index in range(group_number):
            cls.delete_group(api_client, group_index)

    @classmethod
    def create_all_projects(cls, api_client):
        """
        Creates all projects within the dataset
        :param api_client: the APIClient instance that shall be used to create all projects
        :return: nothing
        """
        cls.project_ids = dict()
        cls.create_project(api_client, "hhna", "Высшая нервная деятельность", 0)

        cls.create_project(api_client, "cnl", "Клеточная нейробиология обучения", 0)
        cls.set_permission(api_client, "cnl", 1, "data_process")

        cls.create_project(api_client, "mnl", "Математическая нейробиология обучения", 1)
        cls.set_permission(api_client, "mnl", 0, "data_full")
        cls.set_permission(api_client, "mnl", 2, "data_view")

        cls.create_project(api_client, "mn", "Молекулярная нейробиология", 1)
        cls.set_permission(api_client, "mn", 0, "data_add")
        cls.set_permission(api_client, "mn", 2, "no_access")

        cls.create_project(api_client, "nsw", "Нейробиология сна и бодрствования", 2)
        cls.set_permission(api_client, "nsw", 3, "data_add")

        cls.create_project(api_client, "n", "Нейроонтогенез", 3)
        cls.set_permission(api_client, "n", 2, "full")

        cls.create_project(api_client, "nl", "Нейрофизиология обучения", 3)
        cls.set_permission(api_client, "nl", 4, "data_view")

        cls.create_project(api_client, "gcn", "Общая и клиническая нейрофизиология", 4)
        cls.set_permission(api_client, "gcn", 3, "data_process")

        cls.create_project(api_client, "aphhna", "Прикладная физиология", 4)
        cls.create_project(api_client, "cr", "Условные рефлексы", 4)

    @classmethod
    def delete_all_projects(cls, api_client):
        """
        Deletes all projects within the dataset
        :param api_client: the APIClient instance that shall be used to delete all projects
        :return: nothing
        """
        for project_alias in list(cls.project_ids.keys()):
            cls.delete_project(api_client, project_alias)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        if cls.is_test_applicable():
            EntityViewMixin.throttle_classes = []
            PermissionViewSet.throttle_classes = []
            api_client = APIClient()
            cls.login(api_client)
            cls.load_access_levels(api_client)
            cls.create_all_users(api_client)
            cls.create_all_groups(api_client)
            cls.create_all_projects(api_client)

    def setUp(self):
        if not self.is_test_applicable():
            self.skipTest("All tests within this class have been developed for partial server configuration")

    @classmethod
    def tearDownClass(cls):
        if cls.is_test_applicable():
            api_client = APIClient()
            cls.delete_all_projects(api_client)
            cls.delete_all_groups(api_client)
            cls.delete_all_users(api_client)
        super().tearDownClass()

    def test_user_info_change(self):
        self.change_user_surname(self.client, "ekaterina_mironova", "Иванова",
            command_clue=("usermod", "-c", "Екатерина Иванова,,,", "ekaterina_mironova"))
        self.change_user_surname(self.client, "ekaterina_mironova", "Миронова",
            command_clue=("usermod", "-c", "Екатерина Миронова,,,", "ekaterina_mironova"))

    def test_user_login_change(self):
        self.change_user_login(self.client, "ekaterina_mironova", "user10")
        self.change_user_login(self.client, "user10", "ekaterina_mironova")

    def test_detach_user(self):
        self.detach_user(self.client, 0, "ekaterina_mironova",
            command_queue=("usermod", "-G", "cnl,mnl,mn", "ekaterina_mironova"))
        self.attach_user(self.client, 0, "ekaterina_mironova",
            command_queue=("usermod", "-G", "hhna,mnl,mn,cnl", "ekaterina_mironova"))

    def test_project_update(self):
        self.change_project_alias(self.client, "hhna", "project1")
        self.change_project_alias(self.client, "project1", "hhna")

    def test_permission_delete(self):
        self.delete_permission(self.client, "nsw", 3,
            command_clues=[
                ("usermod", "-G", "cr,gcn,aphhna,n,nl", "ilja_dmitriev"),
                ("usermod", "-G", "cr,gcn,aphhna,n,nl", "anastasia_spiridonova")
            ])
        self.set_permission(self.client, "nsw", 3, "data_add")
