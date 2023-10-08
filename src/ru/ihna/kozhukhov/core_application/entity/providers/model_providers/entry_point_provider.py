from django.utils.module_loading import import_string

from .model_provider import ModelProvider
from ....exceptions.entity_exceptions import CorefacilityModuleDamagedException


class EntryPointProvider(ModelProvider):
    """
    The class is responsible for exchange of information between the EntryPoint entity and the Django model layer.
    """

    _entity_model = "ru.ihna.kozhukhov.core_application.models.EntryPoint"

    _model_fields = ["alias", "name", "type", "entry_point_class", "belonging_module"]

    _lookup_field = "id"
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

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

    def unwrap_entity(self, entity):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        :param entity: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        external_object = super().unwrap_entity(entity)
        # noinspection PyProtectedMember
        if "belonging_module" in entity._edited_fields:
            external_object.belonging_module_id = entity.belonging_module.uuid
        return external_object
