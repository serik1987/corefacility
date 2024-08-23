from django.conf import settings

from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.auto_admin_wrapper_object import \
	AutoAdminWrapperObject
from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.posix_connector import PosixConnector
from ru.ihna.kozhukhov.core_application.management.commands.autoadmin.posix_user import PosixUser
from ...entity_sets.project_set import ProjectSet

from .posix_provider import PosixProvider
from .user_provider import UserProvider


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

	def update_access_level(self, project, group, old_access_level, new_access_level):
		"""
		Provides all POSIX operations related to modification of the project permission.
		:param project: related project
		:param group: group which users must modify their permission.
		:param old_access_level: an access level that is used to be before the level change
		:param new_access_level: desired access level to set by this method
		"""
		if self.is_provider_on():
			old_access_forbidden = old_access_level.alias not in PosixUser.SUPPORTED_ACCESS_LEVELS
			new_access_forbidden = new_access_level.alias not in PosixUser.SUPPORTED_ACCESS_LEVELS
			if old_access_forbidden != new_access_forbidden:
				user_ids = set()
				for user in group.users:
					user_ids.add(user.id)
				connector = AutoAdminWrapperObject(PosixConnector, project.log.id)
				connector.update_connections(list(user_ids))

	def update_group_list(self, user):
		"""
		Updates a group list for a particular user
		:param user: a user which group list must be updated
		:return: nothing
		"""
		if self.is_provider_on():
			user_provider = UserProvider()
			posix_user = user_provider.unwrap_entity(user)
			posix_user.update_supplementary_groups()
