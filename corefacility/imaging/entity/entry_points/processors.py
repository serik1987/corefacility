from core.entity.entry_points.entry_point import EntryPoint
from core.entity.entry_points.projects import ProjectApp

class ProcessorsEntryPoint(EntryPoint):
    """
    A single entry point for all imaging map processors
    """

    def get_alias(self):
        """
        The alias for this entry point is 'processors

        :return: the entry point alias
        """
        return "processors"

    def get_name(self):
        """
        The name of the entry point is "Map processors"

        :return: the entry point name
        """
        return "Imaging processors"

    def get_type(self):
        """
        The entry point type

        :return:
        """
        return "lst"

    def get_parent_module_class(self):
        """
        Returns the parent module class which is always ImagingApp

        :return:
        """
        from imaging import App
        return App

    def is_route_exist(self):
        """
        Defines whether the entry point participates in the API conjunction.
        IF the entry point participates in the API conjunction all modules attached to it must have api_urls
        python's module in their root directory and corefacility's automatic configuration system will organize
        URL paths through this entry point. Also, such paths will be updated during migration of any child application
        :return: True if the entry point participates in the API conjunction, False otherwise
        """
        return True

    def get_parent_module_class(self):
        """
        Returns the parent module for a given entry point. Such a module will be used as an entry point cue

        :return: the parent module or None if no cue shall be provided
        """
        from imaging import App as ImagingApp
        return ImagingApp


class ImagingProcessor(ProjectApp):
    """
    Defines the base class for the imaging processor
    """

    def get_parent_entry_point(self):
        return ProcessorsEntryPoint()

    def is_enabled_by_default(self):
        return True
