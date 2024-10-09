from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RecordSet
from ru.ihna.kozhukhov.core_application.test.entity_set.base_test_class import BaseTestClass

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
