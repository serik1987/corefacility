from enum import Enum

from core.models.enums import LevelType
from core.entity.access_level import AccessLevelSet
from core.entity.entry_points.authorizations import AuthorizationModule
from core.entity.entity_sets.project_application_set import ProjectApplicationSet
from core.entity.project import Project, ProjectSet
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject
from core.test.entity_set.entity_set_objects.project_application_set_object import ProjectApplicationSetObject

from imaging import App as ImagingApp

from .base_test_class import BaseTestClass


class TestApplicationList(BaseTestClass):
    """
    Provides security tests for the ApplicationListView
    """

    PROJECT_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/"
    PROCESSORS_APPLICATION_LIST_PATH = "/api/{version}/core/projects/{project_lookup}/imaging/processors/{data_lookup}/"
    SETTINGS_APPLICATION_LIST_PATH = "/api/{version}/settings/"

    _access_levels = None
    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _project_application_set_object = None

    superuser_required = True
    ordinary_user_required = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._load_access_levels()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())
        cls._project_set_object = ProjectSetObject(cls._group_set_object.clone())
        cls._project_application_set_object = ProjectApplicationSetObject(cls._project_set_object.clone())
        cls.issue_tokens()

    @classmethod
    def _load_access_levels(cls):
        level_set = AccessLevelSet()
        level_set.type = LevelType.app_level
        cls._access_levels = {}
        for level in level_set:
            cls._access_levels[level.alias] = level

    @classmethod
    def issue_tokens(cls):
        for user in cls._user_set_object:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, "%s_token" % user.login, token)

    def test_procesors_list(self, token_id="user1", project="hhna"):
        """
        Tests all available processors
        :param token_id:
        :param project:
        :return:
        """
        pass
        """
        module_list_path = self.PROJECT_APPLICATION_LIST_PATH
        headers = self.get_authorization_headers(token_id)
        project_set = ProjectSet()
        project_set.user = self._user_set_object.get_by_alias("user1")
        project = project_set.get(project)
        for project_app in project.project_apps:
            print(project_app)
            project_app.permissions.set(self._group_set_object[0], self._access_levels['add'])
            for permission in project_app.permissions:
                print(repr(permission))
            print("Project access levels:", Project.get_proper_access_level(project.user_access_level))
            print("Application access level:", project_app.user_access_level)
        """


del BaseTestClass
