from django.utils.translation import gettext
from django.db.models.deletion import RestrictedError
from parameterized import parameterized
from core.models import Project, Module, ProjectPermission, AppPermission, AccessLevel
from core.models.enums import LevelType
from core.test.data_providers.permission_providers import access_level_provider
from .many_group_test import ManyGroupTest

prj = LevelType.project_level
app = LevelType.app_level


class TestPermissions(ManyGroupTest):

    project = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        AccessLevel(type=app.value, alias="another", name="Some another access level").save()
        cls.project = Project(alias="proj", name="proj", root_group=cls.group_list[4])
        cls.project.save()

    @parameterized.expand(access_level_provider())
    def test_project_access_level_list(self, level_slug, expected_level_name, language_code, level_type):
        with self.settings(LANGUAGE_CODE=language_code):
            level = AccessLevel.objects.get(type=level_type.value, alias=level_slug)
            level_name = gettext(level.name)
            self.assertEquals(level_name, expected_level_name)

    @parameterized.expand([(prj, 6), (app, 5)])
    def test_access_level_count(self, level_type, expected_level_count):
        level_count = AccessLevel.objects.filter(type=level_type.value).count()
        self.assertEquals(level_count, expected_level_count)

    def test_root_group_delete(self):
        with self.assertRaises(RestrictedError):
            self.group_list[4].delete()

    def test_project_permission_delete(self):
        level = AccessLevel.objects.get(type="prj", alias="data_view")
        another_level = AccessLevel.objects.get(type="prj", alias="no_access")
        ProjectPermission(project=self.project, group=self.group_list[2], access_level=level).save()
        ProjectPermission(project=self.project, group=self.group_list[0], access_level=another_level).save()
        self.assertEquals(self.project.permissions.count(), 2, "We added two extra permissions to the project. Why "
                                                               "are we seeing another permission number?")
        self.group_list[0].delete()
        self.assertEquals(self.project.permissions.count(), 1,
                          "Initially we had two permissions, we deleted a single group, the permission related to this "
                          "group shall also be deleted. Why didn't it happen?")

    def test_app_level_permission(self):
        sample_app = Module.objects.all()[3]
        AppPermission(application=sample_app, group=self.group_list[0],
                      access_level=AccessLevel.objects.get(type="app", alias="add")).save()
        AppPermission(application=sample_app, group=self.group_list[1],
                      access_level=AccessLevel.objects.get(type="app", alias="permission_required")).save()
        AppPermission(application=sample_app, group=self.group_list[2],
                      access_level=AccessLevel.objects.get(type="app", alias="another")).save()
        AppPermission(application=sample_app, group=self.group_list[3],
                      access_level=AccessLevel.objects.get(type="app", alias="usage")).save()
        AppPermission(application=sample_app, group=self.group_list[4],
                      access_level=AccessLevel.objects.get(type="app", alias="no_access")).save()
        self.assertEquals(sample_app.permissions.count(), 5)
        self.group_list[3].delete()
        self.assertEquals(sample_app.permissions.count(), 4)
