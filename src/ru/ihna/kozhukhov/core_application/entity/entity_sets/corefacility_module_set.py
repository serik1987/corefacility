from uuid import UUID

from django.utils.translation import gettext_lazy as _

from .entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.entity.readers.corefacility_module_reader import CorefacilityModuleReader


class CorefacilityModuleSet(EntitySet):
    """
    Provides a good way to navigate among different corefacility modules
    """

    _entity_name = _("Corefacility module")

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.corefacility_module.CorefacilityModule"

    _entity_reader_class = CorefacilityModuleReader

    _entity_filter_list = {
        "is_root_module": (bool, None),
        "entry_point": ("ru.ihna.kozhukhov.core_application.entity.entry_point.EntryPoint", None),
        "is_enabled": (bool, None),
        "is_application": (bool, None),
        "uuid": (UUID, None)
    }

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        reader = self.entity_reader_class(**self._entity_filters)
        if isinstance(lookup, UUID):
            lookup = str(lookup).replace('-', '')
            source = reader.get(uuid=lookup)
        elif isinstance(lookup, str):
            if lookup != "core" and self.entry_point is None:
                raise ValueError("Searching module by alias is available only in the context of certain entry point")
            source = reader.get(alias=lookup)
        else:
            raise ValueError("To find the module you must provide either its alias or UUID")
        provider = reader.get_entity_provider()
        return provider.wrap_entity(source)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key == "user" and value is not None:
            setattr(self, "is_application", True)
        if key == "project" and value is not None:
            setattr(self, "is_application", True)
        if key == "is_application":
            if not value:
                setattr(self, "user", None)
                setattr(self, "project", None)
