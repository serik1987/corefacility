def slug_provider(max_length):
    """
    Provides the tested slug data

    :param max_length: maximum number of characters in the slug
    :return: list of tuples where the first tuple element is string value and the second tuple element is
        whether such a value is valid
    """
    return [
        ("", False),
        ("a", True),
        ("a" * max_length, True),
        ("a" * (max_length+1), False),
        ("ivanov", True),
        ("IVANOV", True),
        ("Ivanov", True),
        ("iVaNoV", True),
        ("ivanov123", True),
        ("ivanov-ivan", True),
        ("ivanov_ivan", True),
        ("ivanov.ivan", False),
        ("ivanov,ivan", False),
        ("(ivanov-ivan)", False),
        ("иванов-иван", False),
    ]


def arbitrary_string_provider(empty_string_ok, max_string_length):
    """
    Provides the tested string data

    :param empty_string_ok: True if empty strings are allowed. False otherwise
    :param max_string_length: maximum number of characters in the string
    :return: list of tuples where the first tuple element is string value and the second tuple element is
        whether such a value is valid
    """
    return [
        ("", empty_string_ok),
        ("a", True),
        ("a"*max_string_length, True),
        ("a"*(max_string_length+1), False),
        ("Latin", True),
        ("lAtIn", True),
        ("Кириллические буквы", True),
        ("кириллические буквы", True),
        ("1290749*&&^^&", True),
    ]


def email_provider():
    return [
        ("", True),
        ("mail@host.ru", True),
        ("mail@host", False),
        ("sergei.kozhukhov@ihna.ru", True),
        ("sergei_kozhukhov@ihna.ru", True),
        ("sergei-kozhukhov@my-mail.online", True),
        ("мой-аккаунт@домен.рф", False),
        ("my-account", False),
        ("my-account@ihna-ru", False),
    ]


def phone_provider():
    return [
        ("", True),
        ("123", True),
        ("+70000000000", True),
        ("+7 000 000 00 00", True),
        ("+7(000)000-00-00", True),
        ("+7(000) 000 - 0000", True),
        ("kughffd", False),
        ("http:123", False),
        ("+7 123 fkllf", False),
    ]


def boolean_provider():
    """
    Provides sample boolean data

    :return: list of tuples where the first tuple element is string value and the second tuple element is
        whether such a value is valid
    """
    return [
        (True, True),
        (False, True),
        (123, False),
        ("hello", False),
    ]
