import re
import warnings
from uuid import UUID

from django.db import transaction
from django.utils.translation import gettext as _

from ..entity.entity import Entity
from ..entity.fields import ReadOnlyField
from ..entity.providers.model_providers.entry_point_provider import EntryPointProvider
from ..exceptions.entity_exceptions import EntityOperationNotPermitted, EntityNotFoundException, \
    ModuleConstraintFailedException, EntryPointAutoloadFailedException, ModuleInstallationEntryPointException, \
    BelongingModuleIncorrectException, EntryPointAliasIncorrectException, EntryPointDuplicatedException, \
    EntryPointNameIncorrectException, EntryPointTypeIncorrectException
from ..entity.entity_sets.corefacility_module_set import CorefacilityModuleSet
from ..entity.corefacility_module import CorefacilityModule

from ru.ihna.kozhukhov.core_application.entity.entity_sets.entry_point_set import EntryPointSet
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters \
    import AndQueryFilter, StringQueryFilter


class EntryPoint(Entity):
    """
    Entry Point is a special site by which all applications in the 'corefacility' can be interacted with each
    other. The entry points defines both API communication and how some particular application will be embedded
    to the overall user interface
    """

    _entity_set_class = EntryPointSet

    _entity_provider_list = [EntryPointProvider()]

    _required_fields = []

    _state = None
    """ The entry point state """

    _is_parent_module_root = False
    """ The property is used during the autoloading """

    _public_field_description = {
        "belonging_module": ReadOnlyField(description="Module to which this entry point is related"),
        "alias": ReadOnlyField(description="Entry point alias"),
        "name": ReadOnlyField(description="Human-readable name"),
        "type": ReadOnlyField(description="Entry point type"),
        "entry_point_class": ReadOnlyField(description="Entry point application class")
    }

    @classmethod
    def reset(cls):
        """
        Clears the instance that was recently created and/or autoloaded.
        For debugging purpose only.

        Don't forget to delete the instance object after the reset.

        :return: nothing
        """
        if hasattr(cls, "_instance"):
            delattr(cls, "_instance")

    def __new__(cls, *args, **kwargs):
        """
        Entry point is a singleton: only one EntryPoint instance can be created for each entry point class

        :param args: constructor arguments
        :param kwargs: constructor keyword arguments
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(EntryPoint, cls).__new__(cls, *args, **kwargs)
        return getattr(cls, "_instance")

    def __init__(self):
        """
        Initializes the entry point.

        Please, bear in mind that absolutely no arguments are accepted.
        """
        if self._public_fields is None:
            self._public_fields = {}
        if self._edited_fields is None:
            self._edited_fields = set()
        if self._state is None:
            self._state = "found"

    @property
    def id(self):
        """
        Any entry point shall have its unique ID.

        :return: a unique ID of the entry point
        """
        if self._id is None:
            self._autoload()
        return super().id

    @property
    def belonging_module(self):
        """
        Returns the module to which this entry point belongs to

        :return: belonging module of this entry point
        """
        if self._belonging_module is None:
            self._autoload()
        return super().belonging_module

    @property
    def entry_point_class(self):
        """
        The entry point class

        :return: the string connected with the entry point class. Such a string can be substituted to the
        entry point
        """
        return "%s.%s" % (self.__module__, self.__class__.__name__)

    @property
    def alias(self):
        """
        Entry point alias to be used in generation and parsing URLs.
        """
        return self.get_alias()

    @property
    def name(self):
        """
        Human-readable name of the entry point
        """
        return self.get_name()

    @property
    def type(self):
        """
        The entry point type defines how many modules can be attached to this entry point.
        """
        return self.get_type()

    @property
    def state(self):
        """
        State of the entity

        :return: the entry point state
        """
        return self._state

    def get_alias(self):
        """
        Entry point alias is a special name containing letters, digits underscores and/or dashes
        that is used to construct and parse API routes and identifying this particular entry point
        among all similar entry points in the same application

        The entry point alias must be unique across another entry points connected to the same application

        :return: a string containing entry point alias
        """
        raise NotImplementedError("get_alias")

    def get_entity_class_name(self):
        """
        Returns the class name of the current entity

        :return: class name of the current entity
        """
        return _(self.get_name())

    def get_name(self):
        """
        The entry point name defines how the entry point will be displayed in the settings window

        :return: a string containing the entry point name
        """
        raise NotImplementedError("get_name")

    def get_type(self):
        """
        The entry point type can have one of the following values:
        * "lst" - any number of modules can be attached to this entry point and
          any number of modules can be enabled. An example is 'authorizations', 'settings' and 'projects'
          entry point.

        * "sel" - any number of modules can be attached to this entry point
          but just only one module can be enabled. An example is 'synchronizations' entry point that allows to
          download user accounts from the external server.

        :return: the entry point type
        """
        raise NotImplementedError("get_type")

    def get_parent_module_class(self):
        """
        Returns the parent module for a given entry point. Such a module will be used as an entry point cue

        :return: the parent module or None if no cue shall be provided
        """
        warnings.warn("The entry point autoload may be failed because the entry point doesn't belong to the core "
                      "module and get_parent_module returns False. If EntryPointAutoloadFailedException has been "
                      "raised please, re-implement the get_parent_module_class method")
        return None

    def is_route_exist(self):
        """
        Defines whether the entry point participates in the API conjunction.
        IF the entry point participates in the API conjunction all modules attached to it must have api_urls
        python's module in their root directory and corefacility's automatic configuration system will organize
        URL paths through this entry point. Also, such paths will be updated during migration of any child application
        :return: True if the entry point participates in the API conjunction, False otherwise
        """
        return False

    def update(self):
        """
        Changing entry point is not permitted

        :return: nothing
        """
        raise EntityOperationNotPermitted()

    def install(self, belonging_module):
        """
        Installs this particular entry point

        :param: belonging_module the module which this entry point relates to
        :return: nothing
        """
        self._check_preinstall_state()
        self._set_belonging_module(belonging_module)
        self._set_alias()
        self._set_human_readable_name()
        self._set_entry_point_type()
        self._set_database_property("entry_point_class", self.entry_point_class)
        with transaction.atomic():
            self._state = "creating"
            self.create()
            self._state = "found"
            self._autoload()

    def _check_preinstall_state(self):
        """
        Checks the pre-installation state

        :return: nothing
        """
        self._autoload()
        if self.state != "uninstalled":
            raise ModuleInstallationEntryPointException(self)

    def _set_belonging_module(self, module):
        """
        Sets the belonging module during the entry point installation

        :param module: the belonging module
        :return: nothing
        """
        if not isinstance(module, CorefacilityModule):
            raise BelongingModuleIncorrectException(self)
        if not isinstance(module.uuid, UUID):
            raise BelongingModuleIncorrectException(self)
        if module.state != "loaded":
            raise BelongingModuleIncorrectException(self)
        self._set_database_property("belonging_module", module)

    def _set_alias(self):
        """
        Checks and sets the entry point alias

        :return: alias
        """
        desired_alias = self.get_alias()
        if not isinstance(desired_alias, str) or re.match(r'^[\w\-]+$', desired_alias) is None:
            raise EntryPointAliasIncorrectException(self)
        entry_point_set = EntryPointSet()
        entry_point_set.parent_module = self.belonging_module
        try:
            entry_point_set.get(desired_alias)
            raise EntryPointDuplicatedException(self)
        except EntityNotFoundException:
            pass
        self._set_database_property("alias", desired_alias)

    def _set_human_readable_name(self):
        """
        Checks the human-readable name.

        :return: nothing
        """
        desired_name = self.get_name()
        if not isinstance(desired_name, str):
            raise EntryPointNameIncorrectException(self)
        self._set_database_property("name", desired_name)

    def _set_entry_point_type(self):
        """
        Checks the entry point type

        :return: nothing
        """
        from ..models.enums import EntryPointType
        desired_type = self.get_type()
        if not isinstance(desired_type, EntryPointType):
            if not isinstance(desired_type, str):
                raise EntryPointTypeIncorrectException(self)
            try:
                desired_type = EntryPointType(desired_type)
            except ValueError:
                raise EntryPointTypeIncorrectException(self)
        self._set_database_property("type", desired_type)

    def _set_database_property(self, name, value):
        """
        Sets the database property to the module

        :param name: property name
        :param value: property value
        :return: nothing
        """
        setattr(self, '_' + name, value)
        self.notify_field_changed(name)

    def delete(self):
        """
        Deletes the entry point

        :return: nothing
        """
        module_set = CorefacilityModuleSet()
        module_set.entry_point = self
        module = None
        try:
            module = module_set[0]
        except EntityNotFoundException:
            pass
        if module is not None:
            raise ModuleConstraintFailedException(module)
        super().delete()
        self._public_fields = {}
        self._state = "deleted"
        self.__class__.reset()

    def modules(self, is_enabled=True):
        """
        Iterates over all modules attached to this entry point.

        :param is_enabled: True to iterate over all modules where is_enabled property is True. False to iterate over
        all modules
        :return: module iterator
        """
        module_set = CorefacilityModuleSet()
        module_set.entry_point = self
        if is_enabled:
            module_set.is_enabled = True
        for module in module_set:
            yield module

    def widgets(self, is_enabled=True):
        """
        Iterates over all modules attached to this entry point and returns module widgets only.

        :param is_enabled: True to iterate over all modules where is_enabled property is True. False to iterate over
        all modules
        :return: module iterator
        """
        from django.conf import settings
        from django.db import connection
        from django.utils.translation import gettext
        query_builder = settings.QUERY_BUILDER_CLASS()
        query_builder\
            .add_select_expression("uuid")\
            .add_select_expression("alias")\
            .add_select_expression("name")\
            .add_select_expression("html_code")\
            .add_data_source("core_module")\
            .set_main_filter(AndQueryFilter())
        query_builder.main_filter &= StringQueryFilter("parent_entry_point_id=%s", self.id)
        query_builder.main_filter &= ~StringQueryFilter("is_application")
        if is_enabled:
            query_builder.main_filter &= StringQueryFilter("is_enabled")
        query = query_builder.build()
        with connection.cursor() as cursor:
            cursor.execute(query[0], query[1:])
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                uuid = row[0]
                if isinstance(uuid, str):
                    uuid = UUID(uuid)
                yield uuid, row[1], gettext(row[2]), row[3]

    def module(self, alias, is_enabled=True):
        """
        Looks for a module with a given alias attached to this entry point.

        :param alias: alias of the module to find
        :param is_enabled: True - find across all enabled modules, False - find across all modules
        :return: the module found
        """
        module_set = CorefacilityModuleSet()
        module_set.entry_point = self
        if is_enabled:
            module_set.is_enabled = True
        return module_set.get(alias)

    def _autoload(self):
        """
        Automatically loads properties that have not been loaded yet

        :return: nothing
        """
        if self.state in ("deleted", "uninstalled", "creating"):
            return
        entry_point_set = EntryPointSet()
        if self._is_parent_module_root:
            entry_point_set.parent_module_is_root = True
        else:
            parent_module_class = self.get_parent_module_class()
            if parent_module_class is None:
                raise EntryPointAutoloadFailedException(self)
            else:
                entry_point_set.parent_module = parent_module_class()
        entry_point = None
        try:
            entry_point = entry_point_set.get(self.get_alias())
        except EntityNotFoundException:
            self._state = "uninstalled"
        if entry_point is not None and entry_point is not self:
            raise EntryPointAutoloadFailedException(self)
