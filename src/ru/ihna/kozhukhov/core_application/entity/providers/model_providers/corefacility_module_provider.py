from django.utils.module_loading import import_string

from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import CorefacilityModuleDamagedException

from .model_provider import ModelProvider


class CorefacilityModuleProvider(ModelProvider):
    """
    Exchanges important information between the corefacility module and the database using Django model machinery
    """
    
    _entity_model = "ru.ihna.kozhukhov.core_application.models.Module"

    _model_fields = ["alias", "name", "html_code", "app_class", "user_settings", "is_application", "is_enabled",
                     "parent_entry_point"]

    def create_entity(self, module):
        """
        Creates the entity in a certain entity source and changes the entity's _id and _wrapped properties
        according to how the entity changes its status.

        :param module: The entity to be created on this entity source
        :return: nothing but entity provider must fill necessary entity fields
        """
        external_object = self.unwrap_entity(module)
        external_object.save()
        module._uuid = external_object.uuid

    def load_entity(self, module):
        """
        Always return False which means that no corefacility module can be loaded at the level of entity provider.

        The corefacility modules are loaded at the level of entity (see CorefacilityModule._autoload for details)

        :param module: The corefacility module being tried to load
        :return: always None
        """
        return None

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
        module._node_number = external_object.node_number
        module._state = "loaded"
        return module

    def unwrap_entity(self, module):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        :param module: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        if module.state == "creating":
            external_object = self.entity_model()
        else:
            external_object = self.entity_model.objects.get(uuid=module.uuid)
        self._unwrap_entity_properties(external_object, module)
        return external_object
