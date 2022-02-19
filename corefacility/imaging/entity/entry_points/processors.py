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


class ImagingProcessor(ProjectApp):
    """
    Defines the base class for the imaging processor
    """

    def get_parent_entry_point(self):
        return ProcessorsEntryPoint()

    def is_enabled_by_default(self):
        return True
