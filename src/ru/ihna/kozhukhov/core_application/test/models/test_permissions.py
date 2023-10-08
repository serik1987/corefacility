from django.utils.translation import gettext
from django.db.models.deletion import RestrictedError
from parameterized import parameterized
from ...models import Project, AccessLevel
from ..data_providers.permission_providers import access_level_provider
from .many_group_test import ManyGroupTest


# noinspection PyUnresolvedReferences
class TestPermissions(ManyGroupTest):

    project = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        AccessLevel(alias="another", name="Some another access level").save()
        cls.project = Project(alias="proj", name="proj", root_group=cls.group_list[4])
        cls.project.save()

    @parameterized.expand(access_level_provider())
    def test_access_level_list(self, level_slug, expected_level_name, language_code, level_type):
        """
        Tests the entire access level list
        :param level_slug: alias for the access level
        :param expected_level_name: expected name for the access level
        :param language_code: do you want to check 'ru-RU' or 'en-GB' language?
        :param level_type: either project or application access level
        :return:
        """
        with self.settings(LANGUAGE_CODE=language_code):
            level = AccessLevel.objects.get(type=level_type.value, alias=level_slug)
            level_name = gettext(level.name)
            self.assertEquals(level_name, expected_level_name)

    @parameterized.expand([(prj, 6), (app, 3)])
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
