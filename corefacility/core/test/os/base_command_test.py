from django.test import TestCase

from core.os import CommandMaker
from core.os.user import PosixUser


class BaseOsFeatureTest(TestCase):
	_maker = None

	@classmethod
	def setUpTestData(cls):
		super().setUpTestData()
		cls._maker = CommandMaker()
		cls._maker.initialize_executor(cls)

	def setUp(self):
		super().setUp()
		self._maker.initialize_command_queue()
		self.save_initial_users()

	def tearDown(self):
		self._maker.run_all_commands()
		self.restore_initial_users()
		super().tearDown()

	@classmethod
	def tearDownClass(cls):
		cls._maker.clear_executor(cls)
		super().tearDownClass()

	def save_initial_users(self):
		self._initial_users = []
		for user in PosixUser.iterate():
			self._initial_users.append(user.uid)

	def restore_initial_users(self):
		deleting_users = []
		for user in PosixUser.iterate():
			if user.uid not in self._initial_users:
				deleting_users.append(user)
		for user in deleting_users:
			user.delete()
		self._initial_users = None
		self._maker.run_all_commands()
