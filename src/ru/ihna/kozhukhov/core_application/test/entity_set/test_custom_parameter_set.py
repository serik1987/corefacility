import sys

from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RecordSet
from ru.ihna.kozhukhov.core_application.utils import LabjournalCache


from .base_test_class import BaseTestClass
from .entity_set_objects.group_set_object import GroupSetObject
from .entity_set_objects.parameter_descriptor_set_object import ParameterDescriptorSetObject
from .entity_set_objects.project_set_object import ProjectSetObject
from .entity_set_objects.record_set_object import RecordSetObject
from .entity_set_objects.user_set_object import UserSetObject


def parameter_value_provider():
    bool_values = (False, True)
    num_values = [1.0, 2.0, 3.0, 4.0]
    string_values = ["Вася", "Коля", "Петя", "Игорь", "Сильвестр"]
    discrete_values = ['grat', 'ret', 'imag', 'triang', 'video']
    parameter_lists_a = \
        [{'root_bool': value} for value in bool_values] + \
        [{'root_num': value} for value in num_values] + \
        [{'root_string': value} for value in string_values] + \
        [{'root_discrete': value} for value in discrete_values] + \
        [{'a_bool': value} for value in bool_values] + \
        [{'a_num': value} for value in num_values] + \
        [{'a_string': value} for value in num_values] + \
        [{'root_bool': value1, 'root_num': value2} for value1 in bool_values for value2 in num_values] + \
        [{'root_bool': value1, 'root_string': value2} for value1 in bool_values for value2 in string_values] + \
        [{'root_bool': value1, 'root_discrete': value2} for value1 in bool_values for value2 in discrete_values] + \
        [{'root_num': value1, 'root_string': value2} for value1 in num_values for value2 in string_values] + \
        [{'root_num': value1, 'root_discrete': value2} for value1 in num_values for value2 in discrete_values] + \
        [{'root_string': value1, 'root_discrete': value2} for value1 in num_values for value2 in discrete_values] + \
        [{'root_bool': value1, 'a_bool': value2} for value1 in bool_values for value2 in bool_values] + \
        [{'root_num': value1, 'a_num': value2} for value1 in num_values for value2 in num_values] + \
        [{'root_string': value1, 'a_string': value2} for value1 in string_values for value2 in string_values] + \
        [{'root_discrete': value1, 'a_discrete': value2} for value1 in discrete_values for value2 in discrete_values] + \
        [{'root_bool': value1, 'a_num': value2} for value1 in bool_values for value2 in num_values] + \
        [{'root_string': value1, 'a_discrete': value2} for value1 in string_values for value2 in discrete_values] + \
        [{'root_bool': value1, 'a_string': value2} for value1 in bool_values for value2 in string_values] + \
        [{'root_num': value1, 'a_discrete': value2} for value1 in num_values for value2 in discrete_values] + \
        [{'root_bool': value1, 'a_discrete': value2} for value1 in bool_values for value2 in discrete_values] + \
        [{'root_num': value1, 'a_string': value2} for value1 in num_values for value2 in string_values] + \
        [{
            'root_bool': value1,
            'root_num': value2,
            'root_string': value3
        } for value1 in bool_values for value2 in num_values for value3 in string_values] + \
        [{
            'root_bool': value1,
            'root_num': value2,
            'root_string': value3,
            'root_discrete': value4,
        } for value1 in bool_values for value2 in num_values for value3 in string_values for value4 in discrete_values]

    parameter_lists_b = \
        [{'root_bool': value} for value in bool_values] + \
        [{'root_num': value} for value in num_values] + \
        [{'root_string': value} for value in string_values] + \
        [{'root_discrete': value} for value in discrete_values] + \
        [{'b_bool': value} for value in bool_values] + \
        [{'b_num': value} for value in num_values] + \
        [{'b_string': value} for value in num_values] + \
        [{'b_discrete': value} for value in discrete_values] + \
        [{'root_bool': value1, 'root_num': value2} for value1 in bool_values for value2 in num_values] + \
        [{'root_bool': value1, 'root_string': value2} for value1 in bool_values for value2 in string_values] + \
        [{'root_bool': value1, 'root_discrete': value2} for value1 in bool_values for value2 in discrete_values] + \
        [{'root_num': value1, 'root_string': value2} for value1 in num_values for value2 in string_values] + \
        [{'root_num': value1, 'root_discrete': value2} for value1 in num_values for value2 in discrete_values] + \
        [{'root_string': value1, 'root_discrete': value2} for value1 in num_values for value2 in discrete_values]

    logical_operations = [RecordSet.LogicType.AND, RecordSet.LogicType.OR]
    test_types = [BaseTestClass.TEST_ITERATION, BaseTestClass.TEST_COUNT]
    return [
        ('a', parameter_list, logical_operation, test_type)
        for parameter_list in parameter_lists_a
        for logical_operation in logical_operations
        for test_type in test_types
    ] + [
        ('b', parameter_list, logical_operation, test_type)
        for parameter_list in parameter_lists_b
        for logical_operation in logical_operations
        for test_type in test_types
    ]


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

        cls.parent_categories = dict()

        for record in cls._record_set_object.entities:
            if record.level == 1 and record.alias == 'a':
                cls.parent_categories['a'] = record
            elif record.level == 1 and record.alias == 'b':
                cls.parent_categories['b'] = record
            elif record.level == 2 and record.parent_category.alias == 'a':
                if hasattr(record, 'alias') and record.alias == 'a1':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'grat'
                    record.custom_a_bool = False
                    record.custom_a_num = 1
                    record.custom_a_string = "Вася"
                    record.custom_a_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a2':
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a3':
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'imag'
                    record.custom_a_string = "Коля"
                    record.custom_a_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a4':
                    record.custom_root_bool = True
                    record.custom_root_num = 1
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'squares'
                    record.custom_a_bool = True
                    record.custom_a_num = 2
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a5':
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'triang'
                    record.custom_a_string = "Петя"
                    record.custom_a_discrete = 'imag'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a6':
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a7':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'ret'
                    record.custom_a_bool = False
                    record.custom_a_num = 3
                    record.custom_a_string = "Игорь"
                    record.custom_a_discrete = 'squares'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 1":
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'imag'
                    record.custom_a_num = 1
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 2":
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'squares'
                    record.custom_a_string = "Вася"
                    record.custom_a_discrete = 'triang'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 3":
                    record.custom_root_bool = True
                    record.custom_root_num = 1
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'triang'
                    record.custom_a_bool = True
                    record.custom_a_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 4":
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'grat'
                    record.custom_a_num = 2
                    record.custom_a_string = "Коля"
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 5":
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'subcat':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'imag'
                    record.custom_a_bool = False
                    record.custom_a_string = "Петя"
                    record.update()
            elif record.level == 2 and record.parent_category.alias == 'b':
                if hasattr(record, 'alias') and record.alias == 'b1':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'grat'
                    record.custom_b_bool = False
                    record.custom_b_num = 1
                    record.custom_b_string = "Вася"
                    record.custom_b_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b2':
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b3':
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'imag'
                    record.custom_b_string = "Коля"
                    record.custom_b_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b4':
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'squares'
                    record.custom_b_bool = True
                    record.custom_b_num = 2
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b5':
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'triang'
                    record.custom_b_string = "Петя"
                    record.custom_b_discrete = 'imag'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b6':
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b7':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'ret'
                    record.custom_b_bool = False
                    record.custom_b_num = 3
                    record.custom_b_string = "Игорь"
                    record.custom_b_discrete = 'squares'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 1":
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'imag'
                    record.custom_b_num = 1
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 2":
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'squares'
                    record.custom_b_string = "Вася"
                    record.custom_b_discrete = 'triang'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 3":
                    record.custom_root_bool = True
                    record.custom_root_num = 1
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'triang'
                    record.custom_b_bool = True
                    record.custom_b_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 4":
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'grat'
                    record.custom_b_num = 2
                    record.custom_b_string = "Коля"
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 5":
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'subcat':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'imag'
                    record.custom_b_bool = False
                    record.custom_b_string = "Петя"
                    record.update()

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
        # TO-DO:
        # 3. Test all features


del BaseTestClass
