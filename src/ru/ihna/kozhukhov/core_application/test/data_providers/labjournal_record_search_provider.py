from datetime import timedelta

from rest_framework import status

from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType


def category_cue_provider():
    return 'a', 'b', '/a', '/b',

def logic_provider():
    return [
        ('and',),
        ('or',),
    ]

def type_list_provider():
    return (
        [],
        [LabjournalRecordType.data,],
        [LabjournalRecordType.service,],
        [LabjournalRecordType.category,],
        [LabjournalRecordType.data, LabjournalRecordType.service,],
        [LabjournalRecordType.data, LabjournalRecordType.category,],
        [LabjournalRecordType.service, LabjournalRecordType.category],
        [LabjournalRecordType.data, LabjournalRecordType.service, LabjournalRecordType.category,],
    )

def hashtag_list_provider():
    return [
        [],
        ["шахматный"],
        ["редкий"],
        ["редчайший"],
        ["шахматный", "редкий"],
        ["шахматный", "редчайший"],
        ["редкий", "редчайший"],
        ["шахматный", "редкий", "редчайший"],
        ["шахматный", "invalid"],
        ["шахматный", 'kjfhgkfdjh']
    ]

def basic_search_provider():
    tokens_and_responses = [
        ('full', status.HTTP_200_OK,),
        ('data_full', status.HTTP_200_OK,),
        ('data_view', status.HTTP_200_OK,),
        ('no_access', status.HTTP_404_NOT_FOUND,),
    ]
    return [
        (category_cue, token_id, expected_status_code)
        for category_cue in (None, 'a', 'b', 'a/subcat', 'b/subcat', '/a/subcat', '/b/subcat', '/a', '/b')
        for token_id, expected_status_code in tokens_and_responses
    ] + [
        ('optical_imaging:a', 'data_full', status.HTTP_404_NOT_FOUND,),
    ]

def date_search_provider():
    date_range = [
        "2024-01-01T00:00",
        "2024-01-01T12:00",
        "2024-01-02T00:00",
        "2024-01-02T12:00",
        "2024-01-03T00:00",
        None,
    ]
    return [
        (date_from, date_to, category_cue, 'full', status.HTTP_200_OK,)
        for date_from in date_range
        for date_to in date_range
        for category_cue in (None,) + category_cue_provider()
    ]

def hashtag_search_provider():
    return [
        (hashtag_list, hashtag_logic, category_cue, 'full', status.HTTP_200_OK,)
        for hashtag_list in hashtag_list_provider()
        for (hashtag_logic,) in logic_provider()
        for category_cue in category_cue_provider()
    ] + [
        (["шахматный"], 'xor', 'a', 'full', status.HTTP_400_BAD_REQUEST,),
    ]

def types_provider():
    return [
        (record_type, category_cue, 'full', status.HTTP_200_OK,)
        for record_type in type_list_provider()
        for category_cue in category_cue_provider()
    ] + [
        ('data,invalid', 'a', 'full', status.HTTP_400_BAD_REQUEST,),
    ]

def date_from_hashtags_provider():
    dates_hashtag = [
        (5, 5),
        (5, 10),
        (5, None),
        (10, 5),
        (10, 10),
        (10, None),
        (None, 5),
        (None, 10),
    ]
    return [
        (hashtag_list, hashtag_logic, date_from_hashtags, date_to_hashtags, category_cue, 'full', status.HTTP_200_OK,)
        for hashtag_list in hashtag_list_provider()
        for (hashtag_logic,) in logic_provider()
        for date_from_hashtags, date_to_hashtags in dates_hashtag
        for category_cue in category_cue_provider()
    ] + [
        (["шахматный"], 'xor', 5, 10, 'a', 'full', status.HTTP_400_BAD_REQUEST),
        (["шахматный"], 'and', 'abra', 10, 'a', 'full', status.HTTP_400_BAD_REQUEST),
        (["шахматный"], 'and', 5, 'kadabra', 'a', 'full', status.HTTP_400_BAD_REQUEST),
    ]

def custom_parameter_search_provider():
    return [
        (None,  1.0,    'triang',       "Вася",         'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  2.0,    'ret',          "Игорь",        'or',   '/b',   'full',     status.HTTP_200_OK,),
        (False, None,   'grat',         None,           'and',  '/b',   'full',     status.HTTP_200_OK,),
        (True,  3.0,    None,           None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
        (False, 1.0,    'grat',         "Коля",         'or',   '/a',   'full',     status.HTTP_200_OK,),
        (None,  3.0,    None,           "Коля",         'and',  '/b',   'full',     status.HTTP_200_OK,),
        (True,  2.0,    'squares',      "Петя",         'and',  '/b',   'full',     status.HTTP_200_OK,),
        (None,  None,   'squares',      "Вася",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (True,  None,   'ret',          "Коля",         'and',  '/a',   'full',     status.HTTP_200_OK,),
        (None,  2.0,    'triang',       None,           'or',   '/b',   'full',     status.HTTP_200_OK,),
        (False, 1.0,    'squares',      "Коля",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (False, 3.0,    'imag',         "Вася",         'and',  '/b',   'full',     status.HTTP_200_OK,),
        (True,  1.0,    'squares',      None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
        (False, 1.0,    None,           "Игорь",        'and',  '/a',   'full',     status.HTTP_200_OK,),
        (None,  3.0,    'grat',         "Игорь",        'or',   '/a',   'full',     status.HTTP_200_OK,),
        (True,  None,   'imag',         "Игорь",        'or',   '/a',   'full',     status.HTTP_200_OK,),
        (None,  1.0,    'imag',         "Петя",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (False, 2.0,    'grat',         "Петя",         'and',  '/b',   'full',     status.HTTP_200_OK,),
        (None,  1.0,    'ret',          None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
        (True,  2.0,    'imag',         None,           'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  2.0,    'triang',       "Коля",         'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  2.0,    'grat',         "Вася",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (True,  None,   'imag',         "Коля",         'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  2.0,    None,           "Вася",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (False, None,   None,           "Петя",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (True,  3.0,    'squares',      "Игорь",        'and',  '/a',   'full',     status.HTTP_200_OK,),
        (False, 3.0,    'triang',       "Игорь",        'and',  '/a',   'full',     status.HTTP_200_OK,),
        (False, 3.0,    'ret',          "Вася",         'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  None,   'triang',       "Петя",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (True,  3.0,    'ret',          "Петя",         'and',  '/a',   'full',     status.HTTP_200_OK,),
        (False, None,   None,           None,           'and',  '/a',   'full',     status.HTTP_200_OK,),
        (None,  2.0,    None,           None,           'and',  '/b',   'full',     status.HTTP_200_OK,),
        (None,  None,   'squares',      None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
        (None,  None,   None,           "Вася",         'or',   '/b',   'full',     status.HTTP_200_OK,),
        (None,  3.14,   None,           None,           'and',  '/a',   'full',     status.HTTP_200_OK,),
        (None,  None,   'faces',        None,           'and',  '/b',   'full',     status.HTTP_200_OK,),
        (None,  None,   None,           "Юля",          'or',   '/a',   'full',     status.HTTP_200_OK,),
        (True,  1.0,    'squares',      None,           'xor',  '/a',   'full',     status.HTTP_400_BAD_REQUEST,),
        (True,  1.0,    'squares',      None,           'and',  None,   'full',     status.HTTP_200_OK,),
        (True,  1.0,    'squares',      None,           'and', "optical_imaging:a", 'full', status.HTTP_404_NOT_FOUND,),
        ('xxx', 1.0,    'squares',      None,           'and',  '/a',   'full',     status.HTTP_200_OK,),
        ('xxx', 1.0,    'squares',      None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
        (True,  'xxx',  'squares',      None,           'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  'xxx',  'squares',      None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
        (True,  1.0,    'xxx',          None,           'and',  '/a',   'full',     status.HTTP_200_OK,),
        (True,  1.0,    'xxx',          None,           'or',   '/a',   'full',     status.HTTP_200_OK,),
    ]


def relative_date_search_provider():
    date_range = [
        timedelta(0),
        timedelta(hours=6),
        timedelta(hours=12),
        timedelta(hours=18),
        timedelta(hours=24),
    ]
    return [
        (date_from, date_to, category_cue, 'full', status.HTTP_200_OK,)
        for date_from in date_range
        for date_to in date_range
        for category_cue in category_cue_provider()
    ] + [
        (date_from, None, category_cue, 'full', status.HTTP_200_OK,)
        for date_from in date_range
        for category_cue in category_cue_provider()
    ] + [
        (None, date_to, category_cue, 'full', status.HTTP_200_OK,)
        for date_to in date_range
        for category_cue in category_cue_provider()
    ] + [
        (timedelta(hours=6), timedelta(hours=12), None, 'full', status.HTTP_400_BAD_REQUEST,),
        (timedelta(hours=6), timedelta(hours=12), "/a/subcat", 'full', status.HTTP_400_BAD_REQUEST,),
        ('abra', timedelta(hours=12), '/a', 'full', status.HTTP_400_BAD_REQUEST,),
        (timedelta(hours=6), 'kadabra', '/a', 'full', status.HTTP_400_BAD_REQUEST,),
    ]

def name_provider():
    return [
        ("С",),
        ("Служеб"),
        ("Служб",),
        ("Служебная запись 1",),
        ("1",),
    ]
