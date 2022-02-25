from parameterized import parameterized

from core.test.entity_set.base_test_class import BaseTestClass
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject
from core.test.entity_set.entity_set_objects.group_set_object import GroupSetObject
from core.test.entity_set.entity_set_objects.project_set_object import ProjectSetObject
from core.test.entity.entity_objects.corefacility_module_set_object import CorefacilityModuleSetObject
from core.test.entity_set.entity_set_objects.project_application_set_object import ProjectApplicationSetObject
from core.test.data_providers.entity_sets import filter_data_provider


def project_provider():
    return filter_data_provider(
        range(10),
        [
            (BaseTestClass.TEST_COUNT, None, BaseTestClass.POSITIVE_TEST_CASE),
            (BaseTestClass.TEST_ITERATION, None, BaseTestClass.POSITIVE_TEST_CASE),
        ]
    )


class TestProjectFilter(BaseTestClass):
    """
    This is a special class to test the module's project filters
    """

    _user_set_object = None
    _group_set_object = None
    _project_set_object = None
    _corefacility_module_set_object = None
    _project_application_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object.clone())
        cls._project_set_object = ProjectSetObject(cls._group_set_object.clone())
        cls._corefacility_module_set_object = CorefacilityModuleSetObject()
        cls._project_application_set_object = ProjectApplicationSetObject(cls._project_set_object.clone())

    def setUp(self):
        self._container = self._corefacility_module_set_object.clone()

    @parameterized.expand(project_provider())
    def test_project_search(self, project_index, *args):
        project = self._project_set_object[project_index]
        self.apply_filter("project", project)
        self._test_all_access_features(*args)


del BaseTestClass
