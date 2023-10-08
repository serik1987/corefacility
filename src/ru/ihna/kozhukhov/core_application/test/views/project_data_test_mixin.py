from ...entity.access_level import AccessLevelSet
from ...entry_points.authorizations import AuthorizationModule
from ..entity_set.entity_set_objects.user_set_object import UserSetObject
from ..entity_set.entity_set_objects.group_set_object import GroupSetObject
from ..entity_set.entity_set_objects.project_set_object import ProjectSetObject


class ProjectDataTestMixin:
    """
    Contains the create_project_data_environment method that is responsible for creating project data environments.
    Such a method shall be called in the setUpTestData
    """

    _access_levels = None
    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _project_application_set_object = None

    superuser_required = True
    ordinary_user_required = True

    @classmethod
    def create_project_data_environment(cls, create_project_application_set=False):
        cls._load_access_levels()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())
        cls._project_set_object = ProjectSetObject(cls._group_set_object.clone())
        cls.issue_tokens()

    @classmethod
    def _load_access_levels(cls):
        level_set = AccessLevelSet()
        cls._access_levels = {}
        for level in level_set:
            cls._access_levels[level.alias] = level

    @classmethod
    def issue_tokens(cls):
        for user in cls._user_set_object:
            token = AuthorizationModule.issue_token(user)
            setattr(cls, "%s_token" % user.login, token)

    def change_modules_enability(self, project_alias, processors_mode):
        """
        Makes all modules either enabled or disabled
        :param project_alias: project's alias
        :param processors_mode: 'all_enabled', 'all_disabled' or 'none' depending on the action
        :return: nothing
        """
        for project_application_record in self._project_application_set_object:
            if project_application_record.project.alias == project_alias:
                if processors_mode == "all_enabled":
                    project_application_record.is_enabled = True
                    project_application_record.update()
                if processors_mode == "all_disabled":
                    project_application_record.is_enabled = False
                    project_application_record.update()
