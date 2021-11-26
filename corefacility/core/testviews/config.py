from django.http import Http404
from django.shortcuts import render
from django.conf import settings

TEST_CONFIG_TEMPLATE = "core/tests/config.html"
DISPLAY_CONFIGURATION_OPTIONS = [
    'ADMINS',
    'ALLOWED_HOSTS',
    'ALLOWED_IPS',
    'CSRF_USE_SESSIONS',
    'DATABASES',
    'DEBUG',
    'DEFAULT_FROM_EMAIL',
    'SERVER_EMAIL',
    'EMAIL_BACKEND',
    'EMAIL_FILE_PATH',
    'EMAIL_HOST',
    'EMAIL_HOST_PASSWORD',
    'EMAIL_HOST_USER',
    'EMAIL_PORT',
    'EMAIL_SUBJECT_PREFIX',
    'EMAIL_USE_TLS',
    'EMAIL_USE_SSL',
    'INSTALLED_APPS',
    'MIDDLEWARE',
    'LOGGING',
    'MEDIA_URL',
    'MEDIA_ROOT',
    'STATIC_URL',
    'STATIC_ROOT',
    'ROOT_URLCONF',
    'TEMPLATES',
    'USE_I18N',
    'USE_L10N',
    'USE_TZ',
    'AUTHENTICATION_BACKENDS',
    'AUTH_USER_MODEL',
    'LOGOUT_REDIRECT_URL',
    'X_XSS_PROTECTION',
    'SESSION_COOKIE_AGE',
    'SECURE_SSL_REDIRECT',
    'SECURE_SSL_HOST',
    'SECURE_HSTS_SECONDS',
    'SECURE_HSTS_INCLUDE_SUBDOMAINS',
    'SECURE_HSTS_PRELOAD',
    'LANGUAGES',
    'LANGUAGE_CODE',
    'TIME_ZONE',
    'BASE_DIR',
    'CORE_IS_POSIX',
    'CORE_IS_SUDO',
    'CORE_PROJECT_BASEDIR',
    'CORE_MANAGE_UNIX_GROUPS',
    'CORE_MANAGE_UNIX_USERS',
    'CORE_UNIX_ADMINISTRATION',
    'CORE_SUGGEST_ADMINISTRATION',
    'CORE_HARDWARE_DEBUG_MODE',
    'CORE_USER_CAN_CHANGE_HIS_PASSWORD'
]
NO_OPTION_MESSAGE = "No such option exists"


def config(request):
    if not settings.DEBUG:
        raise Http404("Page not found")
    important_config = {}
    for config_name in DISPLAY_CONFIGURATION_OPTIONS:
        try:
            important_config[config_name] = getattr(settings, config_name)
        except AttributeError:
            important_config[config_name] = NO_OPTION_MESSAGE
    return render(request, TEST_CONFIG_TEMPLATE, context={
        "cfg": important_config,
        "no_option_message": NO_OPTION_MESSAGE
    })
