from pathlib import Path

from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import *

def general_data_provider():
    return [
        ('category', 0),
        ('category', 1),
        ('category', 2),
        ('data', 1),
        ('data', 2),
        ('data', 3),
    ]

def general_data_with_path_provider():
    return [
        ('category', 0, '/'),
        ('category', 1, '/adult'),
        ('category', 2, '/adult/rab001'),
        ('data', 1, '/disclaimer'),
        ('data', 2, '/adult/disclaimer'),
        ('data', 3, '/adult/rab001/rec001')
    ]

def base_data_change_provider():
    return [
        ('data', 1, 0, "/disclaimer"),
        ('data', 1, 1, "/disclaimer"),
        ('data', 1, 2, "/disclaimer"),
        ('data', 2, 0, "/adult/disclaimer"),
        ('data', 2, 1, "/new/disclaimer"),
        ('data', 2, 2, "/adult/disclaimer"),
        ('data', 3, 0, "/adult/rab001/rec001"),
        ('data', 3, 1, "/new/rab001/rec001"),
        ('data', 3, 2, "/adult/new/rec001"),
        ('category', 2, 0, "/adult/rab001"),
        ('category', 2, 1, "/new/rab001"),
        ('category', 2, 2, "/adult/new"),
        ('category', 1, 0, "/adult"),
        ('category', 1, 1, "/new"),
        ('category', 1, 2, "/adult"),
        ('category', 0, 0, "/"),
        ('category', 0, 1, "/"),
        ('category', 0, 2, "/"),
    ]

def path_category_change_provider():
    return [
        (record_type, record_index, change_category_index, expected_path, flush)
        for (record_type, record_index, change_category_index, expected_path) in base_data_change_provider()
        for flush in (False, True)
    ]

def descriptor_category_change_provider():
    return [
        (record_type, record_index, change_category_index, change_mode,)
        for record_type, record_index, change_category_index, _ in base_data_change_provider()
        for change_mode in (
            'add',
            'modify',
            'remove',
            'available_value_add',
            'available_value_remove',
            'hashtag_add',
            'hashtag_remove',
            'hashtag_attach',
            'hashtag_detach'
        )
    ]

def find_by_path_provider():
    return [
        ("/", 'category', 0),
        ("/adult", 'category', 1),
        ("/adult/rab001", 'category', 2),
        ("/disclaimer", 'data', 1),
        ("/adult/disclaimer", 'data', 2),
        ("/adult/rab001/rec001", 'data', 3),
    ]

def find_by_path_after_category_change():
    data = [
        (1, '/', None, 'category', 0),
        (1, '/disclaimer', None, 'data', 1),
        (1, '/new', None, 'category', 1),
        (1, '/adult', EntityNotFoundException, None, None),
        (1, '/new/disclaimer', None, 'data', 2),
        (1, '/adult/disclaimer', EntityNotFoundException, None, None),
        (1, '/new/rab001', None, 'category', 2),
        (1, '/adult/rab001', EntityNotFoundException, None, None,),
        (1, '/new/rab001/rec001', None, 'data', 3),
        (1, '/adult/rab001/rec001', EntityNotFoundException, None, None),
        (2, '/', None, 'category', 0),
        (2, '/disclaimer', None, 'data', 1),
        (2, '/adult', None, 'category', 1),
        (2, '/adult/disclaimer', None, 'data', 2),
        (2, '/adult/new', None, 'category', 2),
        (2, '/adult/rab001', EntityNotFoundException, None, None),
        (2, '/adult/new/rec001', None, 'data', 3),
        (2, '/adult/rab001/rec001', EntityNotFoundException, None, None),
    ]
    return [
        (category_to_change, path, exception_to_throw, expected_record_type, expected_record_index, flush)
        for (category_to_change, path, exception_to_throw, expected_record_type, expected_record_index) in data
        for flush in (False, True)
    ]


def custom_field_change_provider():
    float_data = [
        (8.48, 8.48),
        (-8.48, -8.48),
        (6.02e23, 6.02e23),
        (-6.02e23, -6.02e23),
        (6.02e-23, 6.02e-23),
        (-6.02e-23, -6.02e-23),
        (0.0, 0.0),
        (True, 1.0),
        (False, 0.0),
        ("10.3", 10.3),
    ]
    boolean_data = [
        (True, True),
        (False, False),
        (8.48, True),
        (0.0, False),
        ("True", True),
        ("False", True),
        ("", False),
    ]
    string_provider = [
        ("Latin letters", "Latin letters"),
        ("Русские буквы", "Русские буквы"),
        ("123", "123"),
        ("~`!@#$%^&*()_+=-|", "~`!@#$%^&*()_+=-|"),
        ("|\\'\";:/?.>,<", "|\\'\";:/?.>,<"),
        ("буквы ё и Ё", "буквы ё и Ё"),
        ("№", "№",),
        ("", "",),
        ("="*256, "="*256,)
    ]
    assigning_data = [
        (identifier, value, expected_value)
        for identifier in ('custom_cat0_param0', 'custom_cat1_param0', 'custom_cat2_param0')
        for value, expected_value in float_data
    ] + [
        (identifier, value, expected_value)
        for identifier in ('custom_cat0_param24', 'custom_cat1_param24', 'custom_cat2_param24')
        for value, expected_value in boolean_data
    ] + [
        (identifier, value, expected_value)
        for identifier in ('custom_cat0_param12', 'custom_cat1_param12', 'custom_cat2_param12',
                           'custom_cat0_param36', 'custom_cat1_param36', 'custom_cat2_param36')
        for value, expected_value in string_provider
    ]
    return [
        (identifier, value, expected_value, change_mode,)
        for identifier, value, expected_value in assigning_data
        for change_mode in ('on_update', 'on_load')
    ]


def custom_field_for_category_provider():
    return [
        (2, 'custom_cat0_param0', 3.14, 3.14, None),
        (2, 'custom_cat0_param12', "Hello, World!", "Hello, World!", None,),
        (2, 'custom_cat0_param24', True, True, None,),
        (2, 'custom_cat0_param36', "Hello, World!", "Hello, World!", None,),
        (2, 'custom_cat1_param0', 3.14, 3.14, None),
        (2, 'custom_cat1_param12', "Hello, World!", "Hello, World!", None,),
        (2, 'custom_cat1_param24', True, True, None,),
        (2, 'custom_cat1_param36', "Hello, World!", "Hello, World!", None,),
        (2, 'custom_cat2_param0', 3.14, 3.14, None),
        (2, 'custom_cat2_param12', "Hello, World!", "Hello, World!", None,),
        (2, 'custom_cat2_param24', True, True, None,),
        (2, 'custom_cat2_param36', "Hello, World!", "Hello, World!", None,),
        (1, 'custom_cat0_param0', 3.14, 3.14, None),
        (1, 'custom_cat0_param12', "Hello, World!", "Hello, World!", None,),
        (1, 'custom_cat0_param24', True, True, None,),
        (1, 'custom_cat0_param36', "Hello, World!", "Hello, World!", None,),
        (1, 'custom_cat1_param0', 3.14, 3.14, None),
        (1, 'custom_cat1_param12', "Hello, World!", "Hello, World!", None,),
        (1, 'custom_cat1_param24', True, True, None,),
        (1, 'custom_cat1_param36', "Hello, World!", "Hello, World!", None,),
        (1, 'custom_cat2_param0', 3.14, 3.14, AttributeError),
        (1, 'custom_cat2_param12', "Hello, World!", "Hello, World!", AttributeError,),
        (1, 'custom_cat2_param24', True, True, AttributeError,),
        (1, 'custom_cat2_param36', "Hello, World!", "Hello, World!", AttributeError,),
        (0, 'custom_cat0_param0', 3.14, 3.14, AttributeError),
        (0, 'custom_cat0_param12', "Hello, World!", "Hello, World!", AttributeError,),
        (0, 'custom_cat0_param24', True, True, AttributeError,),
        (0, 'custom_cat0_param36', "Hello, World!", "Hello, World!", AttributeError,),
        (0, 'custom_cat1_param0', 3.14, 3.14, AttributeError),
        (0, 'custom_cat1_param12', "Hello, World!", "Hello, World!", AttributeError,),
        (0, 'custom_cat1_param24', True, True, AttributeError,),
        (0, 'custom_cat1_param36', "Hello, World!", "Hello, World!", AttributeError,),
        (0, 'custom_cat2_param0', 3.14, 3.14, AttributeError),
        (0, 'custom_cat2_param12', "Hello, World!", "Hello, World!", AttributeError,),
        (0, 'custom_cat2_param24', True, True, AttributeError,),
        (0, 'custom_cat2_param36', "Hello, World!", "Hello, World!", AttributeError,),
        (2, 'custom_bad_param', "Hello, World", "Hello, World", AttributeError,),
    ]


def default_field_test_provider():
    data = [
        # name           def     cat.1    cat.2    type        Num.  Exp.value
        ('cat0_param0',  0.0,    2.0,     3.0,     'data',     3,    3.0),
        ('cat0_param36', 'Коля', None,    None,    'data',     2,    'Коля'),
        ('cat0_param24', None,   None,    False,   'data',     1,    False),
        ('cat0_param36', None,   'Петя',  'Игорь', 'category', 1,    None),
        ('cat0_param24', False,  True,   None,     'category', 2,    True),
        ('cat0_param24', None,   True,   False,    'data',     2,    True),
        ('cat0_param12', None,   'imag', None,     'service',  None, 'imag'),
        ('cat0_param0',  0.0,    None,   None,     'data',     1,    0.0),
        ('cat0_param24', False,  None,   False,    'category', 0,    False),
        ('cat0_param24', False,  None,   False,    'service',  None, False),
        ('cat0_param12', None,   'imag', 'figu',   'category', 0,    None),
        ('cat0_param12', 'grat', None,   'figu',   'data',     2,    'grat'),
        ('cat0_param0',  None,   None,   None,     'category', 0,    None),
        ('cat0_param0',  None,   2.0,    None,     'data',     2,    2.0),
        ('cat0_param36', 'Коля', 'Петя', 'Игорь',  'category', 0,    'Коля'),
        ('cat0_param36', None,   None,   None,     'service',  None, None),
        ('cat0_param0',  None,   None,   3.0,      'category', 2,    None),
        ('cat0_param12', 'grat', None,   None,     'category', 1,    'grat'),
        ('cat0_param12', 'grat', 'imag', None,     'category', 2,    'imag'),
        ('cat0_param0',  None,   2.0,    None,     'category', 1,    None),
        ('cat0_param24', None,   None,   None,     'data',     3,    False),
        ('cat0_param36', 'Коля', 'Петя', 'Игорь',  'data',     1,    'Коля'),
        ('cat0_param24', None,   True,   None,     'category', 1,    False),
        ('cat0_param0',  0.0,    2.0,    3.0,      'service',  0,    2.0),
        ('cat0_param36', 'Коля', 'Петя', 'Игорь',  'data',     3,    'Игорь'),
        ('cat0_param36', 'Коля', 'Петя', None,     'category', 2,    'Петя'),
        ('cat0_param12', None,   None,   None,     'data',     3,    None),
        ('cat0_param12', 'grat', 'imag', 'figu',   'data',     1,    'grat'),
    ]
    return data

def default_base_directory_provider():
    base_path = Path(settings.LABJOURNAL_BASEDIR)
    return [
        # root base dir     cat.1 b/d   cat.2 b/d   test cat., expected path
        ('../white-rabbit', '.',        None,       0, (base_path / '../white-rabbit').resolve().as_posix()),
        ('.',               'adult',    '../rab1',  2, (base_path / 'rab1').resolve().as_posix()),
        ('../white-rabbit', '../adult', '../rab1',  1, (base_path / '../adult').resolve().as_posix()),
        ('../white-rabbit', None,       'rab1',     2, (base_path / '../white-rabbit/rab1').resolve().as_posix()),
        ('.',               '../adult', 'rab1',     0, base_path.resolve().as_posix()),
        ('.',               '.',        '.',        1, base_path.resolve().as_posix()),
        ('white-rabbit',    '../adult', None,       2, (base_path / 'adult').resolve().as_posix()),
        ('white-rabbit',    None,       '.',        0, (base_path / 'white-rabbit').resolve().as_posix()),
        (None,              None,       None,       1, base_path.resolve().as_posix()),
        ('white-rabbit',    'adult',    None,       1, (base_path / 'white-rabbit/adult').resolve().as_posix()),
        (None,              'adult',    '../rab1',  0, base_path.resolve().as_posix()),
        ('.',               None,       '../rab1',  2, (base_path / '../rab1').resolve().as_posix()),
        ('.',               '.',        None,       2, base_path.resolve().as_posix()),
        (None,              '.',        'rab1',     2, (base_path / 'rab1').resolve().as_posix()),
        (None,              '../adult', '.',        2, (base_path / '../adult').resolve().as_posix()),
        ('../white-rabbit', 'adult',    '.',        2, (base_path / '../white-rabbit/adult').resolve().as_posix()),
        ('white-rabbit',    'adult',    'rab1',     1, (base_path / 'white-rabbit/adult').resolve().as_posix()),
        ('white-rabbit',    '.',        '../adult', 0, (base_path / 'white-rabbit').resolve().as_posix()),
    ]

def categories_with_base_path_provider():
    base_path = Path(settings.LABJOURNAL_BASEDIR)
    return [
        (0, (base_path / "white-rabbit").resolve().as_posix()),
        (1, (base_path / "white-rabbit/adult").resolve().as_posix()),
        (2, (base_path / "white-rabbit/adult/rab1").resolve().as_posix()),
    ]

def file_path_provider():
    base_path = Path(settings.LABJOURNAL_BASEDIR)
    return [
        (1, (base_path / "white-rabbit/neurons.dat").resolve().as_posix()),
        (2, (base_path / "white-rabbit/adult/neurons.dat").resolve().as_posix()),
        (3, (base_path / "white-rabbit/adult/rab1/neurons.dat").resolve().as_posix()),
    ]

def general_data_with_path_and_default_values_provider():
    return [
        ('category', 0, "/",                    0.0,),
        ('category', 1, "/adult",               0.0,),
        ('category', 2, "/adult/rab001",        2.0,),
        ('data',     1, "/disclaimer",          0.0,),
        ('data',     2, "/adult/disclaimer",    2.0,),
        ('data',     3, "/adult/rab001/rec001", 3.0,),
    ]

def find_by_path_then_default_value_provider():
    return [
        ("/",                    'category', 0, 0.0),
        ("/adult",               'category', 1, 0.0),
        ("/adult/rab001",        'category', 2, 2.0),
        ("/disclaimer",          'data',     1, 0.0),
        ("/adult/disclaimer",    'data',     2, 2.0),
        ("/adult/rab001/rec001", 'data',     3, 3.0),
    ]

def data_records_with_default_values_provider():
    return [
        (1, 0.0,),
        (2, 2.0,),
        (3, 3.0,),
    ]
