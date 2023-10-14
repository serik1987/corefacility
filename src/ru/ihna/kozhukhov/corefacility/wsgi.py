"""
WSGI config for corefacility project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

# (1) Selection of proper configuration profile
from .settings.launcher import ConfigLauncher
ConfigLauncher.select_config_profile()

# (2) Embedding the Django settings loader and importing the WSGI application creator.
from configurations.wsgi import get_wsgi_application

# (3) Copying all Django settings from the environment to the corefacility
from django.conf import settings
settings.INSTALLED_APPS

# (4) Creating the WSGI application using the WSGI handler.
application = get_wsgi_application()
