"""
The package is an intermediate between the operating system commands responsible for group create, modify,
update and delete and the corefacility routines.

The goal of the package is to accept requests for the GROUP CRUD operations from any corefacility application
and transform it to the operating system commands which in turn will be sent to the CommandMaker.
"""

from .posix import PosixGroup
from .exceptions import OperatingSystemGroupNotFound
