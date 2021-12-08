class EntryPoint:
    """
    Entry Point is a special site by which all applications in the 'corefacility' can be interacted with each
    other. The entry points defines both API communication and how some particular application will be embedded
    to the overall user interface
    """

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
