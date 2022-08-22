from django.conf import settings

from core.entity.project import ProjectSet
from core.os.user import PosixUser
from core.os.group import PosixGroup

from .posix_provider import PosixProvider


class PermissionProvider(PosixProvider):
	"""
	Adds POSIX users to the group or removes POSIX users from the group connected with some permission changes
	"""

	def is_provider_on(self):
		"""
		True if the provider routines shall be applied, False otherwise
		:return:
		"""
		return not self.force_disable and settings.CORE_MANAGE_UNIX_USERS and \
			settings.CORE_MANAGE_UNIX_GROUPS

	@staticmethod
	def calculate_posix_groups(user):
		"""
		Calculate names of all POSIX groups where the user shall be present in
		:param user: the user that shall be present in certain POSIX groups
		:return: a set containing these POSIX groups
		"""
		project_set = ProjectSet()
		project_set.user = user
		project_groups = [
			project.unix_group for project in project_set
			if project.unix_group is not None and project.unix_group != ""
		]
		return set(project_groups)

	@staticmethod
	def iterate_project_users(project):
		"""
		Iterates over all users that have access to a particular project
		:param project: the project to iterate over
		:return: generator. Use the function result in the for loop to reveal the list of users
		"""
		for group, access_level in project.permissions:
			if access_level.alias != "no_access":
				for user in group.users:
					yield user

	def register_root_group(self, project, posix_group=None):
		"""
		Adds all users from the root group to the project
		:param project: the project which users shall be registered
		:param posix_group: POSIX group related to the project or None if you want to calculate the group automatically
		:return: nothing
		"""
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
		"""
		Provides all POSIX-level operations related to adding some project permission
		:param project: project which permission is intended to be added (an entity)
		:param group: scientific group related to such permission (an entity)
		:return: nothing
		"""
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
		"""
		Provides all POSIX-level operations related to removing some project permissions
		:param project: project which permission is intended to be added (an entity)
		:param group: scientific group related to such permission (an entity)
		:return: nothing
		"""
		if project.unix_group is None or project.unix_group == "" or \
			not self.is_provider_on():
			return
		posix_group = PosixGroup.find_by_name(project.unix_group)
		group_users = posix_group.user_list or list()
		for user in group.users:
			if user.unix_group != "" and user.unix_group is not None and user.unix_group in group_users:
				desired_posix_groups = self.calculate_posix_groups(user)
				if posix_group.name not in desired_posix_groups:
					posix_user = PosixUser.find_by_login(user.unix_group)
					posix_user.set_groups(desired_posix_groups, False)

	def update_group_list(self, user):
		"""
		Updates a group list for a particular user
		:param user: a user which group list must be updated
		:return: nothing
		"""
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
