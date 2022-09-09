import os
import re
import shutil
from importlib import import_module
from pathlib import Path

from django.core.management import CommandError
from django.core.management.commands.makemigrations import Command as BaseCommand
from django.utils.module_loading import import_string


class Command(BaseCommand):
    """
    Makes so called 'installation migrations'

    Installation migrations are such migrations that call application's install() method
    """

    BASE_DIR = Path(__file__).parent.parent.parent.parent.parent
    APPLICATION_LIST_FILE = BASE_DIR / "applications.list"
    MIGRATION_TEMPLATE = BASE_DIR / "corefacility/core/migrations/0002_install.tpl"

    MIGRATIONS_FILE_FORMAT = re.compile(r'^(\d+)_(\w+)\.py$')

    help = "Creates additional migrations that run the application install() function during the database migrations"

    def handle(self, *app_labels, **options):
        app_labels = self.load_app_labels(app_labels)
        for app in app_labels:
            if app == "core":
                self.stdout.write("core: not suitable for making migrations for this module")
                continue
            try:
                migrations_module = import_module("%s.migrations" % app)
            except ModuleNotFoundError:
                self.stdout.write("{module}: 'migrations' package not found. Installation was skipped."
                                  .format(module=app))
                continue
            module_dir = Path(migrations_module.__file__).parent
            migration_list = self.get_migration_list(module_dir)
            if len(migration_list) == 0:
                self.stdout.write("{module}: initial migration not found. Installation was skipped.".format(module=app))
                continue
            if self.install_migration_exists(migration_list):
                self.stdout.write("{module}: migration already exists. Installation was skipped.".format(module=app))
                continue
            max_migration_number = max(migration_list.keys())
            install_migration_name = "%04d_install.py" % (max_migration_number + 1)
            install_migration_filename = os.path.join(module_dir, install_migration_name)
            self.make_install_migration(app, install_migration_filename)
            self.stdout.write("{module}: building install migrations completed.".format(module=app))

    def load_app_labels(self, app_labels):
        if not app_labels:
            if not os.path.isfile(self.APPLICATION_LIST_FILE):
                raise CommandError("Please, configure the system by using the 'configure' command")
            with open(self.APPLICATION_LIST_FILE, "r") as app_list_file:
                app_labels = app_list_file.read().split("\n")
        return app_labels

    def get_migration_list(self, module_dir):
        migration_list = dict()
        for file in os.listdir(module_dir):
            file_info = self.MIGRATIONS_FILE_FORMAT.match(file)
            if file_info is None:
                continue
            migration_number = int(file_info[1])
            migration_name = file_info[2]
            migration_list[migration_number] = migration_name
        return migration_list

    def install_migration_exists(self, migration_list):
        for value in migration_list.values():
            if value == "install":
                return True
        return False

    def make_install_migration(self, app_module, install_migration_filename):
        shutil.copyfile(self.MIGRATION_TEMPLATE, install_migration_filename)
        app_class = import_string("%s.App" % app_module)
        app = app_class()
        parent_app_class = app.get_parent_entry_point().get_parent_module_class()
        parent_app_id = parent_app_class.__module__.split(".")[-1]
        with open(install_migration_filename, "r") as install_migration_file:
            content = install_migration_file.read() \
                .replace("{{app_name}}", app.name) \
                .replace("{{app_module}}", app_module.split(".")[-1]) \
                .replace("{{parent_app_module}}", parent_app_id)
        with open(install_migration_filename, "w") as install_migration_file:
            install_migration_file.write(content)
