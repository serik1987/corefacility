from importlib import import_module
from ipaddress import ip_network

from django.conf import settings

from ru.ihna.kozhukhov.core_application.entity.entity import Entity


def serialize_all_args(*args, **kwargs):
    """
    Serialize the method arguments to such a way as we can store them to the database

    :param args: function arguments to serialize
    :param kwargs: function keyword arguments to serialize
    :return: a Python dict containing the serialized versions of the object
    """
    return {
        "args": serialize_args(args),
        "kwargs": serialize_args(kwargs),
    }

def deserialize_all_args(obj):
    """
    Deserialize the method arguments previously stored in the database

    :param obj: the serialized version of method arguments stored in the database
    :return: a tuple (positioned_arguments, keyword_arguments). The first element is tuple while the second one
        is dictionary.
    """
    return (
        tuple(deserialize_args(obj['args'])),
        deserialize_args(obj['kwargs']),
    )


def serialize_args(args):
    """
    Recursive serialization of argument|arguments used for the method or class constructor call

    :param args: method argument or arguments to be serialized
    :return: a Python primitive containing serialized version of such an argument / arguments
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


def deserialize_args(obj):
    """
    Recursive deserialization of argument/arguments for the method or class constructor call

    :param obj: a Python primitive containing serialized version of such an argument / arguments
    :return: method argument or arguments to be deserialized
    """
    if isinstance(obj, dict):
        if sorted(obj.keys()) == ['entity_class', 'entity_id']:
            entity_set_module_name, entity_set_class_name = obj['entity_class'].rsplit('.', 1)
            entity_set_module = import_module(entity_set_module_name)
            entity_set_class = getattr(entity_set_module, entity_set_class_name)
            entity = entity_set_class().get(obj['entity_id'])
            return entity
        else:
            return {name: deserialize_args(value) for name, value in obj.items()}
    elif isinstance(obj, list):
        return [deserialize_args(item) for item in obj]
    else:
        return obj


def check_allowed_ip(ip):
    """
    Checks whether the IP address is within the set of allowed IP addresses

    :param ip: the IP address to check
    :return: True if the IP address is within the set, False otherwise
    """
    ip_is_allowed = False
    for allowed_ip in settings.ALLOWED_IPS:
        if ip in ip_network(allowed_ip, False):
            ip_is_allowed = True
    return ip_is_allowed
