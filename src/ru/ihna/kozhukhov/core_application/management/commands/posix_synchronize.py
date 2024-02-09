import os
import subprocess

from django.core.management import BaseCommand

from .autoadmin.posix_group import PosixGroup
from ...entity.user import UserSet
from ...entity.project import ProjectSet
from .autoadmin.posix_user import PosixUser
from ...exceptions.entity_exceptions import PosixCommandFailedException


class Command(BaseCommand):
    """
    Provides synchronization between POSIX accounts and corefacility accounts
    """

    _corefacility_users = None
    _corefacilility_projects = None

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.

        :param args: position arguments for this command
        :param options: optional arguments for this command
        """
        self._initialize_users_and_projects()
        self._update_user_list()
        self._clear_bad_links()
        self._update_project_list()
        self._update_connections()

    def add_record(self, severity, message):
        """
        Prints the log record on the screen

        :param severity: the severity level
        :param message: the message to print
        """
        print("[%s] %s" % (severity, message))

    def _initialize_users_and_projects(self):
        """
        Initialize all protected fields within the command
        """
        self._corefacility_users = UserSet()
        self._corefacility_users.is_support = False
        self._corefacility_projects = ProjectSet()

    def _clear_bad_links(self):
        """
        Clears all invalid links in home directories of all users
        """
        for corefacility_user in self._corefacility_users:
            posix_user = PosixUser(corefacility_user)
            posix_user.command_emulation = False
            posix_user.log = self
            for filename_short in os.listdir(corefacility_user.home_dir):
                filename = os.path.join(corefacility_user.home_dir, filename_short)
                if not os.path.islink(filename):
                    continue
                target = os.readlink(filename)
                if not os.path.exists(target):
                    posix_user.run(('rm', '-rf', filename))

    def _update_user_list(self):
        """
        Establishes consistency between corefacility users and POSIX users
        """
        for corefacility_user in self._corefacility_users:
            posix_user = PosixUser(corefacility_user)
            posix_user.command_emulation = False
            posix_user.log = self
            available_posix_user = posix_user.check_user_for_update()
            if available_posix_user is None:
                posix_user.create()
            elif not os.path.isdir(posix_user.home_dir):
                    posix_user.run(('userdel', '-rf', posix_user.login))
                    posix_user.create()
            try:
                posix_user.update_lock()
            except PosixCommandFailedException:
                print("[WARN] The user has been created but it still locked.")

    def _update_project_list(self):
        """
        Establishes consistency between corefacility projects and POSIX groups
        """
        for corefacility_project in self._corefacility_projects:
            posix_group = PosixGroup(corefacility_project)
            posix_group.command_emulation = False
            posix_group.log = self
            available_posix_group = posix_group.check_group_for_update()
            if available_posix_group is None:
                posix_group.create()
            elif not os.path.isdir(posix_group.project_dir):
                posix_group.run(('groupdel', posix_group.name))
                posix_group.create()

    def _update_connections(self):
        """
        Updates connections between POSIX users and POSIX groups
        """
        for corefacility_user in self._corefacility_users:
            posix_user = PosixUser(corefacility_user)
            posix_user.command_emulation = False
            posix_user.log = self
            posix_user.update_supplementary_groups()
