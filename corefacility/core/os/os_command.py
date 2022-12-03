from django.conf import settings
from django.core.management import BaseCommand

from .command_maker import CommandMaker


class OsCommand(BaseCommand):
	"""
	This is a base class for all commands that request the operating system features
	through the CommandMaker. Make this class as superclass of your Django CLI command
	if you cope with the following problem:
		- the command is failed in partial server configuration;
		- the command is failed because CommandMaker has not been initialized
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		settings.CORE_UNIX_ADMINISTRATION = True
		settings.CORE_SUGGEST_ADMINISTRATION = False
		maker = CommandMaker()
		maker.initialize_executor(self)