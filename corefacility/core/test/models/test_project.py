from django.db.utils import IntegrityError
from django.test import TestCase
from parameterized import parameterized
from core.models import Project, User, Group, GroupUser


class TestProject(TestCase):
    """
    This class provides facilities for testing the Project model
    """
    user = None
    group = None

    LOGIN = "sergei"
    GROUP_NAME = "Optical imaging"

    @classmethod
    def setUpTestData(cls):
        cls.user = User(login=cls.LOGIN)
        cls.user.save()
        cls.group = Group(name=cls.GROUP_NAME, id=1000)
        cls.group.save()
        GroupUser(group=cls.group, user=cls.user, is_governor=True).save()

    def test_user_precondition(self):
        user = User.objects.get(login=self.LOGIN)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.login, self.LOGIN, "The login of the preconditioned user must be properly saved")
        for null_field in ['password_hash', 'name', 'surname', 'email', 'phone', 'unix_group',
                           'home_dir', 'activation_code_hash', 'activation_code_expiry_date']:
            self.assertIsNone(getattr(user, null_field),
                              "The field '%s' for precondition user must be null" % null_field)
        self.assertFalse(user.is_locked, "The user can't be automatically locked")
        self.assertFalse(user.is_superuser, "User can't be automatically become a superuser")
        self.assertFalse(user.is_support, "Users can't be added to the technical support")
        self.assertEqual(user.avatar.name, "", "The user must have no avatar")
        self.assertIsNotNone(user.groups.get(group=self.group), "The precondition user must be included into one "
                                                                "precondition group")

    def test_group_precondition(self):
        group = Group.objects.get(name=self.GROUP_NAME)
        self.assertEqual(group.id, self.group.id, "The precondition group must be saved to the database")
        self.assertIsNotNone(group.users.get(user=self.user), "The precondition group must contain at least one user")

    def test_sample_project(self):
        project = Project(alias="vasomotor-oscillations", name="Vasomotor Oscillations",
                          root_group=self.group)
        project.save()
        another_project = Project.objects.get(id=project.id)
        self.assertMandatoryProperties(project, another_project)
        self.assertEmptyAvatar(another_project)
        self.assertEmptyDescription(another_project)
        self.assertNoExtraInvasions(another_project)
        project.delete()
        self.assertEquals(Project.objects.count(), 0,
                          "The project must be properly deleted after completion of this test")
        self.assertNumQueries(100)

    @parameterized.expand([
        ("alias", "some-slug_1009", None),
        ("alias", None, IntegrityError),
        ("name", "Мой проект № 1-SUPER", None),
        ("description", "Поэма Льва Николаевича Толстого 'Война и мир'", None),
        ("project_dir", "grp-vasomotor-oscillations", None),
    ])
    def test_standard(self, name, value, expected_exception):
        project = Project(alias="some-project-slug", name="Some Project Name", root_group=self.group)
        setattr(project, name, value)
        if expected_exception:
            with self.assertRaises(expected_exception):
                project.save()
        else:
            project.save()
            another_project = Project.objects.get(id=project.id)
            self.assertEquals(value, getattr(another_project, name), "The field '%s' was stored incorrectly" % name)
            self.assertMandatoryProperties(project, another_project)
            self.assertEmptyAvatar(another_project)
            if name == "description":
                self.assertEquals(another_project.description, value, "The project description doesn't properly saved")
            else:
                self.assertEmptyDescription(another_project)
            if name == "project_dir":
                self.assertEquals(another_project.project_dir, value, "The project directory doesn't saved correctly")
            elif name == "unix_group":
                self.assertEquals(another_project.unix_group, value, "The user group doesn't saved correctly")
            else:
                self.assertNoExtraInvasions(another_project)

    def test_alias_duplication(self):
        with self.assertRaises(IntegrityError):
            for n in range(2):
                Project(alias="-", name="Some Project Alias", root_group=self.group).save()

    def test_name_duplication(self):
        with self.assertRaises(IntegrityError):
            for alias in ["alias1", "alias2"]:
                Project(alias=alias, name="Some Project", root_group=self.group).save()

    def test_another_duplication(self):
        for alias, name in [("alias1", "name1"), ("alias2", "name2")]:
            Project(alias=alias, name=name, root_group=self.group).save()

    def test_no_group(self):
        with self.assertRaises(IntegrityError):
            Project(alias="ijod", name="lishvk").save()

    def test_fake_group(self):
        with self.assertRaises(ValueError):
            group = Group(name="super")
            Project(alias="super", name="super", root_group=group).save()

    def assertMandatoryProperties(self, project, another_project):
        self.assertEqual(another_project.alias, project.alias, "The project alias must be correctly saved")
        self.assertEquals(another_project.name, project.name, "The project name must be correctly saved")
        self.assertEquals(another_project.root_group.id, self.group.id, "Precondition group must be assigned to our "
                                                                        "project")

    def assertEmptyAvatar(self, another_project):
        self.assertEquals(another_project.avatar.name, "", "The avatar field must be empty")

    def assertEmptyDescription(self, another_project):
        self.assertIsNone(another_project.description, "The default project description must not exists")

    def assertNoExtraInvasions(self, another_project):
        self.assertEquals(another_project.permissions.count(), 0,
                          "Another groups must be added to the project automatically")
        self.assertEquals(another_project.project_apps.count(), 0,
                          "No applications must be automatically added to the project")
        self.assertIsNone(another_project.project_dir, "By default, the project directory is None")
        self.assertIsNone(another_project.unix_group, "By default, no UNIX group is assigned to the project")
        self.assertEquals(Project.objects.count(), 1,
                          "No any other projects must be automatically added to the database")
