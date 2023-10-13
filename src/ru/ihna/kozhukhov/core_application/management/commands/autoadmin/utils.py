from ru.ihna.kozhukhov.core_application.entity.entity import Entity


def serialize_all_args(*args, **kwargs):
    """
    Serialize the method transform arguments to such a way as we can store them to the database

    :param args: function arguments to serialize
    :param kwargs: function keyword arguments to serialize
    :return: a Python dict containing the serialized versions of the object
    """
    return {
        "args": serialize_args(args),
        "kwargs": serialize_args(kwargs),
    }


def serialize_args(args):
    """
    Recursive serialization of argument|arguments used for the method or class constructor call

    :param args: method argument or arguments to be serialized
    :return: a Python primitive containing serialized version of such an argument | arguments
    """
    if isinstance(args, list) or isinstance(args, tuple):
        return [serialize_args(arg) for arg in args]
    elif isinstance(args, dict):
        return {name: serialize_args(value) for name, value in args.items()}
    elif isinstance(args, Entity):
        entity_set = args.get_entity_set_class()
        return {'entity_class': "{0}.{1}".format(entity_set.__module__, entity_set.__name__), 'entity_id': args.id}
    else:
        return args
