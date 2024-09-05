from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import (
    EntityOperationNotPermitted,
    EntityFieldInvalid,
)
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from ..entity.base_test_class import BaseTestClass as FieldTester
from .field_value_providers import put_stages_in_provider
from ...models import LabjournalRecord


def category_provider():
    return [
        ('data_record', FieldTester.TEST_CREATE_AND_LOAD, None,),
        ('level1', FieldTester.TEST_CREATE_LOAD_AND_CHANGE, EntityOperationNotPermitted,),
        ('level0', FieldTester.TEST_CREATE_CHANGE_AND_LOAD, EntityOperationNotPermitted,),
        ('level0', FieldTester.TEST_CREATE_AND_LOAD, None,),
        ('level2', FieldTester.TEST_CREATE_AND_LOAD, None,),
        ('str', FieldTester.TEST_CREATE_CHANGE_AND_LOAD, EntityFieldInvalid,),
        ('level0', FieldTester.TEST_CREATE_LOAD_AND_CHANGE, EntityOperationNotPermitted,),
        ('level1', FieldTester.TEST_CHANGE_CREATE_AND_LOAD, None,),
        ('level2', FieldTester.TEST_CREATE_LOAD_AND_CHANGE, EntityOperationNotPermitted,),
        ('str', FieldTester.TEST_CREATE_AND_LOAD, None,),
        ('level2', FieldTester.TEST_CHANGE_CREATE_AND_LOAD, None,),
        ('level1', FieldTester.TEST_CREATE_CHANGE_AND_LOAD, EntityOperationNotPermitted,),
        ('data_record', FieldTester.TEST_CHANGE_CREATE_AND_LOAD, EntityFieldInvalid,),
        ('data_record', FieldTester.TEST_CHANGE_CREATE_AND_LOAD, EntityFieldInvalid,),
        ('str', FieldTester.TEST_CREATE_LOAD_AND_CHANGE, EntityFieldInvalid,),
        ('level0', FieldTester.TEST_CHANGE_CREATE_AND_LOAD, None,),
        ('level1', FieldTester.TEST_CREATE_AND_LOAD, None,),
        ('str', FieldTester.TEST_CHANGE_CREATE_AND_LOAD, EntityFieldInvalid,),
        ('level2', FieldTester.TEST_CREATE_CHANGE_AND_LOAD, EntityOperationNotPermitted,),
        ('data_record', FieldTester.TEST_CREATE_LOAD_AND_CHANGE, EntityFieldInvalid,),
    ]

def identifier_provider():
    data = [
        (123, EntityFieldInvalid,),
        (None, EntityFieldInvalid,),
        ("", EntityFieldInvalid,),
        ("a", None,),
        ("a" * 256, None,),
        ("a" * 257, EntityFieldInvalid,),
        ("small_literals", None),
        ("LARGE_LITERALS", None),
        ("small_and_LARGE_literals", None),
        ("digits_123", None,),
        ("noundescore", None,),
        ("_underscore", EntityFieldInvalid,),
        ("1first_digit", EntityFieldInvalid,),
        ("identifier$", EntityFieldInvalid,),
        ("identifier^", EntityFieldInvalid,),
        ("identifier&", EntityFieldInvalid,),
        ("identifier(", EntityFieldInvalid,),
        ("identifier)", EntityFieldInvalid,),
        ("identifier{", EntityFieldInvalid,),
        ("identifier}", EntityFieldInvalid,),
        ("small-literals", EntityFieldInvalid,),
        ("small.literals", EntityFieldInvalid,),
        ("small,large_literals", EntityFieldInvalid,),
        ("identifier!", EntityFieldInvalid,),
        ("русские_буквы", EntityFieldInvalid,),
    ]
    return put_stages_in_provider(data)

def record_type_provider():
    data = [
        ([LabjournalRecordType.data], [], None,),
        ([LabjournalRecordType.service], [LabjournalRecordType.data], None,),
        ([LabjournalRecordType.data], [LabjournalRecordType.service], None,),
        ([LabjournalRecordType.data], [LabjournalRecordType.category], None,),
        ([LabjournalRecordType.data], [LabjournalRecordType.data, LabjournalRecordType.service], None,),
        ([LabjournalRecordType.data], [LabjournalRecordType.data, LabjournalRecordType.category], None,),
        ([LabjournalRecordType.data], [LabjournalRecordType.service, LabjournalRecordType.category], None,),
        (
            [LabjournalRecordType.data],
            [LabjournalRecordType.data, LabjournalRecordType.service, LabjournalRecordType.category],
            None,
        ),
        ([LabjournalRecordType.data, LabjournalRecordType.data], [LabjournalRecordType.data], None,),
        ([LabjournalRecordType.data, "Hello, World!"], [LabjournalRecordType.data], EntityFieldInvalid,),
        (LabjournalRecordType.data, LabjournalRecordType.service, None,),
        ("Hello, World!", LabjournalRecordType.service, EntityFieldInvalid,),
    ]
    return put_stages_in_provider(data)

def value_alias_provider():
    return [
        ("some-slug", None),
        (None, EntityFieldInvalid),
        ("LARGECAPS", None),
        ("smallcaps", None),
        ("---------", None),
        ("123", None),
        ("_____", None),
        (".....", None),
        (",,,,,", EntityFieldInvalid),
        ("$$$", EntityFieldInvalid),
        ("///", EntityFieldInvalid),
        ("\\\\\\", EntityFieldInvalid),
        (":::", EntityFieldInvalid),
        ("%%%", EntityFieldInvalid),
        ("^^^", EntityFieldInvalid),
        ("   ", EntityFieldInvalid),
        ("\n", EntityFieldInvalid),
        ("^^^", EntityFieldInvalid),
        ("псевдоним", EntityFieldInvalid),
        ("' OR 1=1; --", EntityFieldInvalid),
        ("", EntityFieldInvalid),
        ("-", None),
        ("-"*256, None),
        ("-"*257, EntityFieldInvalid),
    ]

def value_description_provider():
    return [
        ("Latin letters", None),
        ("Русские буквы", None),
        ("123", None),
        ("~`!@#$%^&*()_+=-|", None),
        ("|\\'\";:/?.>,<", None),
        ("буквы ё и Ё", None),
        ("№", None),
        (None, EntityFieldInvalid),
        ("", EntityFieldInvalid),
        ("Я", None),
        ("Я" * 256, None),
        ("Я" * 257, EntityFieldInvalid),
    ]

def default_value_provider_for_number_provider():
    data = [
        (10.0, 3.14, None,),
        (10.0, 0.0, None,),
        (10.0, -3.14, None,),
        (10.0, 6.02e23, None,),
        (10.0, -6.02e23, None,),
        (10.0, 6.02e-23, None,),
        (10.0, -6.02e-23, None,),
        (10.0, None, None,),
        ("hello, world!", 10.0, ValueError,),
    ]
    return put_stages_in_provider(data)

def default_value_for_discrete_provider():
    data = [
        ('cw', 'cw', None,),
        ('cw', 'ccw', None,),
        ('ccw', 'cw', None,),
        ('ccw', 'ccw', None,),
        ('', 'cw', EntityFieldInvalid,),
        ('bad_value', 'cw', EntityFieldInvalid,),
        ('-'*257, 'cw', EntityFieldInvalid,),
        (None, 'cw', None,),
        ('cw', None, None,),
    ]
    return [
        data_arguments + (stage_argument,)
        for data_arguments in data
        for stage_argument in (
            FieldTester.TEST_CREATE_AND_LOAD,
            FieldTester.TEST_CREATE_CHANGE_AND_LOAD,
            FieldTester.TEST_CREATE_LOAD_AND_CHANGE,
        )
    ]
