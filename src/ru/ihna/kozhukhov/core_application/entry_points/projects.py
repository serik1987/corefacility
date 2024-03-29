from django.utils.translation import gettext_lazy as _


from ..entity.corefacility_module import CorefacilityModule
from ru.ihna.kozhukhov.core_application.entity.entry_point import EntryPoint


class ProjectsEntryPoint(EntryPoint):
    """
    Creates new entry point for the projects.

    All application that deal with science rather than perform administrative tasks must be connected
    to this entry point or to any application the deal with science rather than perform administrative tasks
    """

    _is_parent_module_root = True
    """ The property is used during the autoloading """

    def get_alias(self):
        """
        Alias of this entry point is always the same: 'projects'

        :return: the entry point alias
        """
        return "projects"

    def get_name(self):
        """
        The name of the entry point visible from the UI

        :return: the entry point name
        """
        _("Project applications")
        return "Project applications"

    def get_type(self):
        return "lst"

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
        from .. import App as CoreApp
        return CoreApp


class ProjectApp(CorefacilityModule):
    """
    This is a base class for all "Project applications". The project applications are attached to the
    "project" entry point, can interact with the project, all their views provides the all necessary
    authorization routines. However, the application developer can add his new own routines
    """

    def get_parent_entry_point(self):
        return ProjectsEntryPoint()

    def get_html_code(self):
        """
        The only HTML code for the project application is their names.
        Any other codes were omitted for the sake of simplicity

        :return: the project HTML code
        """
        return None

    @property
    def is_application(self):
        """
        This is the application: superuser can control its access and attachment
        to any other projects

        :return: True
        """
        return True
