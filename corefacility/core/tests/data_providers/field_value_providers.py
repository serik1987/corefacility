from core.entity.entity_exceptions import EntityFieldInvalid


def put_stages_in_provider(data):
    final_data = []
    for dataset in data:
        for stage in range(4):
            final_data.append(dataset + (stage,))
    return final_data


def alias_provider(min_length, max_length):
    data = [
        ("some-slug", "some-slug", None),
        (None, "some-slug", EntityFieldInvalid),
        ("LARGECAPS", "some-slug", None),
        ("smallcaps", "some-slug", None),
        ("---------", "some-slug", None),
        ("123", "some-slug", None),
        ("_____", "some-slug", None),
        (".....", "some-slug", None),
        (",,,,,", "some-slug", EntityFieldInvalid),
        ("$$$", "some-slug", EntityFieldInvalid),
        ("///", "some-slug", EntityFieldInvalid),
        ("\\\\\\", "some-slug", EntityFieldInvalid),
        (":::", "some-slug", EntityFieldInvalid),
        ("%%%", "some-slug", EntityFieldInvalid),
        ("^^^", "some-slug", EntityFieldInvalid),
        ("   ", "some-slug", EntityFieldInvalid),
        ("\n", "some-slug", EntityFieldInvalid),
        ("^^^", "some-slug", EntityFieldInvalid),
        ("псевдоним", "some-slug", EntityFieldInvalid),
        ("' OR 1=1; --", "some-slug", EntityFieldInvalid),
    ]
    if min_length is not None and min_length > 0:
        data.append(("-" * min_length, "some-slug", None))
        data.append(("-" * (min_length-1), "some-slug", EntityFieldInvalid))
    min_length = 0
    if max_length is not None and max_length >= min_length:
        data.append(("-" * max_length, "some-slug", None))
        data.append(("-" * (max_length+1), "some-slug", EntityFieldInvalid))
    return put_stages_in_provider(data)


def string_provider(min_length, max_length):
    data = [
        ("Latin letters", "Some text", None),
        ("Русские буквы", "Some text", None),
        ("123", "Some text", None),
        ("~`!@#$%^&*()_+=-|", "Some text", None),
        ("|\\'\";:/?.>,<", "Some text", None),
        ("буквы ё и Ё", "Some text", None),
        ("№", "Some text", None),
    ]
    if min_length is not None and min_length > 0:
        data.append(("-" * min_length, "text", None))
        data.append(("-" * (min_length-1), "text", EntityFieldInvalid))
    min_length = 0
    if max_length is not None and max_length >= min_length:
        data.append(("-" * max_length, "text", None))
        data.append(("-" * (max_length+1), "text", EntityFieldInvalid))
    return put_stages_in_provider(data)


def boolean_provider():
    data = [
        (True, False, None),
        (False, True, None),
    ]
    return put_stages_in_provider(data)
