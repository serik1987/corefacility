import os
import re
import shutil
import subprocess
from importlib import import_module
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    """
    Builds all React JS projects and writes JS and CSS static files based on such a build
    """

    base_dir_environment_variable = 'COREFACILITY_SETTINGS_DIR'
    frontend_files_template = re.compile("^.+\\..+\\.(js|css)(\\.map)?$")

    base_dir = None
    apps_dir = None
    base_frontend_lib_dir = None


    def add_arguments(self, parser: CommandParser):
        """
        Adds arguments to the command line parser

        :param parser: a command line parser to which the argument shall be added
        :return: None
        """
        parser.add_argument("application", nargs="*",
                            help="Applications which frontends shall be built. Please, not that each application must "
                                 "have related React JS project within the frontend/apps directory. If this argument "
                                 "is omitted, the command will build all registered applications.")
        parser.add_argument("-b", "--base-dir",
                            help="The project root directory. Please, note that React.JS projects for all applications"
                                 "to build must be located in the frontend/apps directory relatively to this one")


    def handle(self, application, base_dir, *args, **options):
        """
        Main function for the request handling

        :param application: a list that contains names of all applications to build. Empty list means we will build
            all applications
        :param base_dir: base directory for the project
        """
        self._get_base_dir(base_dir)
        applications = self._get_frontend_applications(application)
        for application_name, frontend_path in applications.items():
            self._build_single_application(application_name, frontend_path)

    def _get_base_dir(self, base_dir):
        """
        Retrieves the base directory

        :param base_dir: base directory for the project as if it passed though the argument
        :return: None
        """
        if base_dir is not None:
            self.base_dir = Path(base_dir)
        else:
            settings_dir = os.environ.get(self.base_dir_environment_variable)
            if settings_dir is not None:
                self.base_dir = Path(settings_dir).parent
            else:
                self.base_dir = Path(os.getcwd())
        self.apps_dir = self.base_dir / 'frontend' / 'apps'
        self.base_frontend_lib_dir = self.base_dir / 'frontend' / 'common_components'
        if not os.path.isdir(self.apps_dir):
            raise CommandError("{0} is not base directory because {1} doesn't exist".\
                               format(self.base_dir, self.apps_dir))

    def _get_frontend_applications(self, application: list) -> dict:
        """
        Returns a list of frontend applications required for the build

        :param application: a list that contains names of all applications to build. Empty list means we will build
            all applications
        :return: a dictionary application name => frontend directory
        """
        if application is None or len(application) == 0:
            application = settings.INSTALLED_APPS
        application_list = dict()
        for application_name in application:
            frontend_path = self.apps_dir / application_name
            if os.path.isdir(frontend_path):
                application_list[application_name] = frontend_path
        return application_list

    def _build_single_application(self, application_name: str, frontend_path: Path) -> None:
        """
        Constructs a single application

        :param application_name: name of the application to build
        :param frontend_path: a path where the frontend is located
        """
        static_files_dir = Path(import_module(application_name).__file__).parent / 'static' / application_name
        self.remove_old_frontend(static_files_dir)
        self.copy_base_frontend_lib(frontend_path)
        self.run_npm_build(frontend_path)
        self.copy_new_frontend(frontend_path, static_files_dir)

    def remove_old_frontend(self, static_files_dir: Path) -> None:
        """
        Removes old frontend files

        :param static_files_dir: directory where old frontend files are located
        :return: None
        """
        for old_frontend_file in os.listdir(static_files_dir):
            if self.frontend_files_template.search(old_frontend_file) is not None:
                os.remove(static_files_dir / old_frontend_file)

    def copy_base_frontend_lib(self, frontend_path: Path) -> None:
        """
        Copies the base frontend library (so called 'corefacility-base') to the source directory
        """
        target_base_library_dir = frontend_path / 'src' / 'corefacility-base'
        shutil.rmtree(target_base_library_dir)
        shutil.copytree(self.base_frontend_lib_dir, target_base_library_dir)

    def run_npm_build(self, project_dir):
        """
        Builds the React.js project

        :param project_dir: a project directory to build
        """
        return_code = subprocess.call(
            ('npm', 'run', 'build'),
            cwd=project_dir
        )
        if return_code != 0:
            raise CommandError("Building {0}: Building the NPM project has been failed.".format(project_dir))

    def copy_new_frontend(self, project_path, static_files_dir):
        """
        Copies the newly built frontend files to the static files directory

        :param project_path: project root directory
        :param static_files_dir: directory where Django static files are located.
        """
        files_to_copy = [
            *[
                project_path / 'build' / 'static' / 'js' / filename
                for filename in os.listdir(project_path / 'build' / 'static' / 'js')
            ],
            *[
                project_path / 'build' / 'static' / 'css' / filename
                for filename in os.listdir(project_path / 'build' / 'static' / 'css')
            ]
        ]
        for file_to_copy in files_to_copy:
            if file_to_copy.name.endswith('LICENSE.txt'):
                continue
            shutil.copy(file_to_copy, static_files_dir)
