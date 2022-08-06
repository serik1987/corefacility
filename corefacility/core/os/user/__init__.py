"""
The package is an intermediate between the operating system commands and the other application modules
for the purpose of adding, retrieving, modifying the deleting the users in the operating system.

The goal of the package is to accept requests from the other application module, transform them to the
operating system commands and send them to the core.os.CommandMaker component, accept and parse command
results, send such results to the application modules.
"""

from .posix import PosixUser
from .exceptions import OperatingSystemUserNotFoundException, OperatingSystemUserLoginTooLarge
