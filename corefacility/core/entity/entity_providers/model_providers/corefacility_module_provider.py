from django.utils.module_loading import import_string

from core.entity.entity_exceptions import CorefacilityModuleDamagedException

from .model_provider import ModelProvider


class CorefacilityModuleProvider(ModelProvider):
    """
    Exchanges important information between the corefacility module and the database using Django model machinery
    """

    def wrap_entity(self, external_object):
        """
        When the entity information is loaded from the external source, some external_object
        is created (e.g., a django.db.models.Model for database entity provider or dict for
        POSIX users provider). The goal of this function is to transform such external object
        to the entity.

        This method is called by the EntityReader and you are also free to call this method
        by the load_entity function.

        To create the entity using the wrap_entity method use the Entity constructor in the
        following way:
        entity = Entity(_src=external_object, field1=value1, field2=value2, ...)

        In this case,
        - the entity state will be 'loaded' rather than 'creating';
        - the entity _wrapped field will be assigned to this particular object

        :param external_object: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        module_class = import_string(external_object.app_class)
        module = module_class()
        if module.alias != external_object.alias or \
                module.name != external_object.name or \
                module.html_code != external_object.html_code or \
                module.is_application != external_object.is_application:
            raise CorefacilityModuleDamagedException()
        module._uuid = external_object.uuid
        module._alias = external_object.alias
        module._name = external_object.name
        module._html_code = external_object.html_code
        module._app_class = external_object.app_class
        module._user_settings = external_object.user_settings
        module._is_application = external_object.is_application
        module._is_enabled = external_object.is_enabled
        module._state = "loaded"
        return module
