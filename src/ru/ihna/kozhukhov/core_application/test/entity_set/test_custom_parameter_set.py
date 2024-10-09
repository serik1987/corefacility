import sys

from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.utils import LabjournalCache


from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.parameter_descriptor_set_object import ParameterDescriptorSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject
from ..data_providers.custom_parameter_value_provider import parameter_value_provider


class TestCustomParameterSet(BaseTestClass):
    """
    This class doesn't test the entity set. However, it tests searching facilities over custom parameters
    """

    @classmethod
    def setUpTestData(cls):
        """
        Executes before all tests
        """
        super().setUpTestData()

        LabjournalCache().flush()

        cls._user_set_object = UserSetObject()
        cls._group_set_object = GroupSetObject(cls._user_set_object)
        cls._project_set_object = ProjectSetObject(cls._group_set_object)
        cls._record_set_object = RecordSetObject(cls._user_set_object, cls._project_set_object)
        cls._parameter_descriptor_set_object = ParameterDescriptorSetObject(cls._record_set_object)
        cls.parent_categories = cls._parameter_descriptor_set_object.set_custom_parameters()

    def setUp(self):
        super().setUp()
        self._container = TestCustomParameterSet._record_set_object.clone()
        self._container.sort()
        self.initialize_filters()

    @parameterized.expand(parameter_value_provider())
    def test_custom_parameter_value(self, parent_category_alias, parameter_list, logical_operation, test_type):
        """
        Tests a set of 'custom_xxx' filters

        :param parent_category_alias: alias of the parent category
        :param parameter_list: list of custom parameter to adjust. Such a list must be inputted in the form of
            identifier => value dictionary where identifier is parameter identifier and value is value to use for
            the filtration
        :param logical_operation: the logical operation to apply: RecordSet.LogicType.AND or RecordSet.LogicType.OR
        :param test_type: what type of test to use: BaseTestClass.ITERATION or BaseTestClass.COUNT
        """
        custom_filter = parameter_list.copy()
        custom_filter['_logic'] = logical_operation
        parent_category = self.parent_categories[parent_category_alias]
        self.apply_filter('parent_category', parent_category)
        self.apply_filter('custom_parameters', custom_filter)
        self._test_all_access_features(test_type, None, TestCustomParameterSet.POSITIVE_TEST_CASE)


del BaseTestClass
