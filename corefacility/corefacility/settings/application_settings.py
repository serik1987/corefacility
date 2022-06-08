import sys
from logging.handlers import SysLogHandler

INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        'django.contrib.messages',
        'rest_framework',
        'core',
        'authorizations.google',
        'authorizations.mailru',
        'authorizations.ihna',
        'authorizations.cookie',
        'imaging',
        'roi',
]

MIDDLEWARE = [
    'core.middleware.LogMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "debug_filter": {
            "()": "corefacility.log.DebugFilter",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        }
    },
    "formatters": {
        "console_formatter": {
            "()": "corefacility.log.ConsoleFormatter",
            "format": "[%(asctime)s] %(name)s:\t(%(levelname)s) %(message)s",
        },
        "syslog_formatter": {
            "format": "%(name)s[%(levelname)s]: %(message)s"
        },
        "database_log_formatter": {
            "format": "[%(name)s] %(message)s"
        }
    },
    "handlers": {
        "stream_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console_formatter",
            "filters": ["debug_filter"],
        },
        "syslog_handler": {
            "class": "logging.handlers.SysLogHandler",
            "level": "WARNING",
            "formatter": "syslog_formatter",
            "facility": "local1",
            "address": "/dev/log"
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "database_log_handler": {
            "class": "corefacility.log.DatabaseHandler",
            "level": "DEBUG",
            "filters": ["debug_filter"],
        }
    },
    "loggers": {
        "django.corefacility": {
            "level": "DEBUG",
            "propagate": False,
            "filters": [],
            "handlers": ["stream_handler", "syslog_handler", "mail_admins", "database_log_handler"],
        },
        "django.corefacility.log": {
            "level": "CRITICAL",
            "propagate": False,
            "handlers": ["stream_handler", "syslog_handler", "mail_admins"],
        }
    }
}

if sys.platform.startswith("win32"):
	del LOGGING["handlers"]["syslog_handler"]
	LOGGING["loggers"]["django.corefacility"]["handlers"].remove("syslog_handler")
	LOGGING["loggers"]["django.corefacility.log"]["handlers"].remove("syslog_handler")
