from django.utils.module_loading import import_string

from .model_provider import ModelProvider
from ...entity_exceptions import CorefacilityModuleDamagedException


class EntryPointProvider(ModelProvider):
    """
    The class is responsible for exchange of information between the EntryPoint entity and the Django model layer.
    """

    _entity_model = "core.models.EntryPoint"

    _model_fields = ["alias", "name", "type", "entry_point_class", "belonging_module"]

    def wrap_entity(self, external_object):
        """
        Transforms some object loaded from the database to the entry point

        :param external_object: the external object to transform
        :return: an EntryPoint instance
        """
        ep_class = import_string(external_object.entry_point_class)
        entry_point = ep_class()
        if entry_point.get_alias() != external_object.alias:
            raise CorefacilityModuleDamagedException()
        if entry_point.get_type() != external_object.type:
            raise CorefacilityModuleDamagedException()
        if entry_point.get_name() != external_object.name:
            raise CorefacilityModuleDamagedException()
        belonging_module_class = import_string(external_object.belonging_module_class)
        entry_point._belonging_module = belonging_module_class()
        entry_point._id = external_object.id
        entry_point._state = 'loaded'
        return entry_point
