from django.conf import settings

from core.models.enums import LevelType
from core.entity.user import User
from core.entity.group import Group
from core.entity.project import Project, ProjectSet
from core.entity.project_application import ProjectApplication
from core.entity.access_level import AccessLevelSet
from core.entity.entity_providers.posix_providers.posix_provider import PosixProvider
from core.entity.entity_providers.file_providers.files_provider import FilesProvider
from core.entity.entry_points.authorizations import AuthorizationModule
from core.os import CommandMaker


class ProjectDataTestMixinSmall:
    """
    Creates so called 'small test environment' for the project data. Such environment diminishes number of test cases
    but is not suitable for permission pairwise tests.

    The mixin contains the create_test_environment class method that you need to include into the
    setUpTestData and the destroy_test_environment class method to be included into the tearDownClass
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

    projects = None

    application = None
    """ Application to be tested """

    @classmethod
    def create_test_environment(cls, project_number=1):
        """
        Creates the test environment
        :param project_number: number of projects to create
        """
        if not settings.CORE_SUGGEST_ADMINISTRATION:
            PosixProvider.force_disable = False
            FilesProvider.force_disable = False
        executor = list()
        maker = CommandMaker()
        maker.initialize_executor(executor)
        cls.load_access_levels()
        cls.create_users_and_groups()
        cls.create_projects(project_number)
        cls.attach_application()
        maker.clear_executor(executor)

    def initialize_projects(self):
        """
        If you use projects array, please, call this method at test's setUp
        """
        project_set = ProjectSet()
        self.projects = [project_set.get(project_id) for project_id in self.projects]

    @classmethod
    def destroy_test_environment(cls):
        """
        Destroys the test environment
        """
        executor = list()
        maker = CommandMaker()
        maker.initialize_executor(executor)
        for project in cls.projects:
            if not isinstance(project, Project):
                project = ProjectSet().get(project)
            project.delete()
        cls.delete_users_and_groups()
        maker.clear_executor(executor)

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
    def create_projects(cls, project_number=1):
        """
        Creates test project and sets proper permissions
        :param project_number: total number of projects
        """
        cls.projects = []
        for project_index in range(project_number):
            project_alias = "test_project%d" % project_index if project_index > 0 else "test_project"
            project = Project(alias=project_alias, name=project_alias, root_group=cls.group_list['full'])
            project.create()
            for login, group in cls.group_list.items():
                if login not in ("superuser", "full", "ordinary_user"):
                    project.permissions.set(group, cls.access_levels[login])
            if project_index == 0:
                cls.project = project
            cls.projects.append(project.id)

    @classmethod
    def attach_application(cls, application=None):
        """
        Attaches application to the project
        :param application: application to be attached or None to attach application mentioned in the application
            public property
        """
        if application is None:
            application = cls.application
        for project_id in cls.projects:
            project = ProjectSet().get(project_id)
            project_application = ProjectApplication(application=application, project=project, is_enabled=True)
            project_application.create()

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
