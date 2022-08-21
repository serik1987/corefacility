from django.conf import settings

from core.entity.project import ProjectSet
from core.os.user import PosixUser
from core.os.group import PosixGroup

from .posix_provider import PosixProvider

class PermissionProvider(PosixProvider):

	def is_provider_on(self):
		return not self.force_disable and settings.CORE_MANAGE_UNIX_USERS and \
			settings.CORE_MANAGE_UNIX_GROUPS

	def calculate_posix_groups(self, user):
		project_set = ProjectSet()
		project_set.user = user
		project_groups = [
			project.unix_group for project in project_set
			if project.unix_group is not None and project.unix_group != ""
		]
		return set(project_groups)

	def iterate_project_users(self, project):
		for group, access_level in project.permissions:
			if access_level.alias != "no_access":
				for user in group.users:
					yield user

	def register_root_group(self, project, posix_group=None):
		if not self.is_provider_on():
			return
		if posix_group is None:
			posix_group = PosixGroup.find_by_name(project.unix_group)
		actual_users = posix_group.user_list
		if actual_users is None:
			actual_users = set()
		desired_users = {
			user.unix_group for user in project.root_group.users
			if user.unix_group is not None and user.unix_group != ""
		}
		if actual_users != desired_users:
			for user in project.root_group.users:
				posix_user = PosixUser.find_by_login(user.unix_group)
				posix_user.set_groups([project.unix_group], True)

	def insert_group(self, project, group):
		if project.unix_group is None or project.unix_group == "" or \
			not self.is_provider_on():
			return
		posix_group = PosixGroup.find_by_name(project.unix_group)
		group_users = posix_group.user_list or list()
		for user in group.users:
			if user.unix_group != "" and user.unix_group is not None:
				posix_user = PosixUser.find_by_login(user.unix_group)
				if posix_user.login not in group_users:
					posix_user.set_groups([project.unix_group], True)

	def remove_group(self, project, group):
		if project.unix_group is None or project.unix_group == "" or \
			not self.is_provider_on():
			return
		posix_group = PosixGroup.find_by_name(project.unix_group)
		group_users = posix_group.user_list or list()
		for user in group.users:
			if user.unix_group != "" and user.unix_group is not None:
				if user.unix_group in group_users:
					desired_posix_groups = self.calculate_posix_groups(user)
					if posix_group.name not in desired_posix_groups:
						posix_user = PosixUser.find_by_login(user.unix_group)
						posix_user.set_groups(desired_posix_groups, False)

	def update_group_list(self, user):
		if user.unix_group is None or user.unix_group == "" or not self.is_provider_on():
			return
		posix_user = PosixUser.find_by_login(user.unix_group)
		desired_groups = self.calculate_posix_groups(user)
		actual_groups = set()
		for group in PosixGroup.iterate():
			if user.unix_group in group.user_list:
				actual_groups.add(group.name)
		if actual_groups != desired_groups:
			posix_user.set_groups(desired_groups, False)
