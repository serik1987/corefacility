from core.entity.entity import Entity
from core.entity.entity_fields import ReadOnlyField
from core.entity.entity_exceptions import EntityOperationNotPermitted
from .entry_point_set import EntryPointSet


class EntryPoint(Entity):
    """
    Entry Point is a special site by which all applications in the 'corefacility' can be interacted with each
    other. The entry points defines both API communication and how some particular application will be embedded
    to the overall user interface
    """

    _entity_set_class = EntryPointSet

    _entity_provider_list = []   # TO-DO: define proper entity provider

    _required_fields = []

    _is_installing = False
    """ True if entry point is currently installing to the application """

    _public_fields = {
        "belonging_module": ReadOnlyField(description="Module to which this entry point is related"),
        "alias": ReadOnlyField(description="Entry point alias"),
        "name": ReadOnlyField(description="Human-readable name"),
        "type": ReadOnlyField(description="Entry point type"),
    }

    def __new__(cls, *args, **kwargs):
        """
        Entry point is a singleton: only one EntryPoint instance can be created for each entry point class

        :param args: constructor arguments
        :param kwargs: constructor keyword arguments
        """
        if not hasattr(cls, "_instance"):
            cls._instance = super(EntryPoint, cls).__new__(cls, *args, **kwargs)
        return getattr(cls, "_instance")

    def get_alias(self):
        """
        Entry point alias is a special name containing letters, digits underscores and/or dashes
        that is used to construct and parse API routes and identifying this particular entry point
        among all similar entry points in the same application

        The entry point alias must be unique across another entry points connected to the same application

        :return: a string containing entry point alias
        """
        raise NotImplementedError("get_alias")

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

    def create(self):
        """
        Creates entry point if and only if this is currently installing

        :return: nothing
        """
        if not self._is_installing:
            raise EntityOperationNotPermitted()
        super().create()

    def update(self):
        """
        Changing entry point is not permitted

        :return: nothing
        """
        raise EntityOperationNotPermitted()

    def install(self):
        """
        Installs this particular entry point

        :return: nothing
        """
        raise NotImplementedError("TO-DO: install entry point")
