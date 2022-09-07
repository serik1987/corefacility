from core.entity.entry_points.projects import ProjectApp
from .entity.entry_points.processors import ProcessorsEntryPoint


class App(ProjectApp):
    """
    A base class for the imaging app that adjusts its interactions with the core application module
    """

    def get_alias(self):
        """
        Returns the project alias

        :return: the project alias
        """
        return "imaging"

    def get_name(self):
        """
        Returns the project name

        :return: the project name
        """
        return "Basic functional maps processing"

    def is_enabled_by_default(self):
        """
        Returns True because we need to demonstrate that our 'corefacility' application is very, very useful

        :return: True
        """
        return True

    def get_entry_points(self):
        """
        The application provides common routines for map loading, saving, uploading, downloading and visualizing.
        Any complex map processing shall be organized in stand-alone application attached to this entry point

        :return: a single entry point where all map processors can be attached
        """
        return {
            "processors": ProcessorsEntryPoint()
        }

    def get_serializer_class(self):
        """
        Returns the serializer for the application settings retrieval/updating
        """
        from core.serializers import ApplicationSettingsSerializer
        return ApplicationSettingsSerializer
