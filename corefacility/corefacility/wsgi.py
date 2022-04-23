"""
WSGI config for corefacility project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

from colorama import init
init()
from corefacility.settings_launcher import select_config_profile
select_config_profile()
from configurations.wsgi import get_wsgi_application
application = get_wsgi_application()
