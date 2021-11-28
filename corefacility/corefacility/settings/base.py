import os
from pathlib import Path
from configurations import Configuration, values
from configurations.utils import uppercase_attributes
from django.core.exceptions import ImproperlyConfigured
from . import application_settings


class CorefacilityConfiguration(Configuration):
    """
    Defines base application settings valid for any configuration profile
    """

    # directory where .env files are located (not a Django option)
    settings_dir = "settings"

    # extension of .env files (not a Django option)
    settings_file_extension = ".env"

    # the preliminary settings file will be ignored since it has already been loaded and applied
    preliminary_settings_file = "preliminary.env"

    # the author of this application. He must receive an E-mail in case of some critical errors
    author = ("Sergei Kozhukhov", "sergei.kozhukhov@ihna.ru")

    # True if ADMIN_NAME and ADMIN_EMAIL options shall be considered, False otherwise.
    admin_allowed = False

    # Name of the web server administrator
    ADMIN_NAME = values.Value(None)

    # E-mail of the web server administrator
    ADMIN_EMAIL = values.EmailValue(None)

    # The list of allowed hosts (values of the Host request header). All requests related to any other hosts will
    # be declined
    ALLOWED_HOSTS = values.ListValue(["localhost", "127.0.0.1", "[::1]"])

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # The debug mode
    DEBUG = values.BooleanValue(False)

    # The language that will be used to output all messages
    LANGUAGE_CODE = values.Value("en-us")

    # Time zone: required for correct time representation
    TIME_ZONE = values.Value("America/Chicago")

    # Use sessions to save the CSRF token
    CSRF_USE_SESSIONS = True

    # The SQL backend
    SQL_BACKEND = values.Value(None)

    # The SQL name
    SQL_NAME = values.Value(None)

    # the SQL server
    SQL_SERVER = values.Value(None)

    # the port listened by the SQL server
    SQL_PORT = values.IntegerValue(1)

    # the SQL user
    SQL_USER = values.Value("root")

    # the SQL password
    SQL_PASSWORD = values.Value("")

    # Default primary key field type
    # https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    # defines a basic WSGI application
    WSGI_APPLICATION = 'corefacility.wsgi.application'

    # defines a Python module where basic location-to-views mapping is provided
    ROOT_URLCONF = 'corefacility.urls'

    # The value of the From field
    DEFAULT_FROM_EMAIL = values.Value("webmaster@localhost")
    
    # Defines the E-mail backend
    EMAIL_BACKEND = values.Value(None, environ_required=True)

    # Defines directory where all e-mails shall be sent
    EMAIL_FILE_PATH = values.Value("")

    # SMTP server address
    EMAIL_HOST = values.Value("localhost")

    # SMTP server post
    EMAIL_PORT = values.PositiveIntegerValue(25)

    # SMTP login credentials
    EMAIL_HOST_USER = values.Value("")
    EMAIL_HOST_PASSWORD = values.Value("")

    # Using TLS/SSL
    EMAIL_USE_TLS = values.BooleanValue(False)
    EMAIL_USE_SSL = values.BooleanValue(False)

    # Permanent properties to load static files
    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "corefacility/static")
    ]
    MEDIA_URL = '/media/'

    # Location of static and media files
    STATIC_ROOT = values.Value("")
    MEDIA_ROOT = values.Value("")

    # Template processing properties
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    # Permanent localization settings
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Secret key
    SECRET_KEY = values.Value()

    # Security means
    SECURE_SSL_REDIRECT = values.BooleanValue(False)
    SECURE_SSL_HOSTNAME = values.Value("")
    SECURE_HSTS_SECONDS = values.IntegerValue(0)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = values.BooleanValue(False)
    SECURE_HSTS_PRELOAD = values.BooleanValue(False)

    # List of files that are needed to fully perform the administrative functions
    admin_files = {
        "/etc/passwd": os.R_OK | os.W_OK,
        "/etc/shadow": os.R_OK | os.W_OK,
        "/etc/group": os.R_OK | os.W_OK,
        "/home": os.R_OK | os.W_OK | os.X_OK
    }

    # Authorization password validators
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    @classmethod
    def pre_setup(cls):
        """
        Loads default configuration settings from the .env files

        :return: Nothing
        """
        if cls.DOTENV_LOADED is None:
            base_dir = os.path.join(Path(cls.BASE_DIR).parent, cls.settings_dir)
            if not os.listdir(base_dir):
                os.mkdir(base_dir)
            for filename in os.listdir(base_dir):
                if filename.endswith(cls.settings_file_extension) and filename != cls.preliminary_settings_file:
                    cls.DOTENV = os.path.join(base_dir, filename)
                    cls.load_dotenv()

    @classmethod
    def setup(cls):
        """
        Defines the basic configuration settings in the following way
        1) all settings that are defined through the environment variables will be copied from the environment
        2) if certain settings are not compatible with a definitive configuration profile MalformedConfiguration raises
        3) the remaining configuration settings will be copied from the

        :return: Nothing
        """
        super().setup()
        cls.check_config_possibility()
        cls.load_application_settings()

    @classmethod
    def check_config_possibility(cls):
        """
        Checks whether the configuration profile is applicable. If not throws MalformedConfiguration

        :return: Nothing.
        """
        pass

    @classmethod
    def check_posix(cls):
        """
        Throws an exception if the server is not deployed under POSIX operating system

        :return: Nothing
        """
        if not cls.CORE_IS_POSIX():
            print("This configuration profile is not available in non-POSIX operating system")
            raise ImproperlyConfigured()

    @classmethod
    def check_sudo(cls):
        """
        Throws an exception if the server doesn't have an access to administrative functions

        :return: Nothing
        """
        if not cls.CORE_IS_SUDO():
            print("The worker process EUID doesn't correspond to root. Select another "
                  "configuration profile run the app in docker or run it under sudo to overcome this problem.")
            raise ImproperlyConfigured()

    @classmethod
    def load_application_settings(cls):
        """
        Loads settings from application_settings module

        :return: Settings from the application_settings module
        """
        for name, value in uppercase_attributes(application_settings).items():
            setattr(cls, name, value)

    def ADMINS(self):
        """
        Some Django configuration properties are defined as methods

        :return: list of admins to e-mail
        """
        admin_list = [self.author]
        if self.admin_allowed and self.ADMIN_NAME is not None and self.ADMIN_EMAIL is not None:
            admin_list.append((self.ADMIN_NAME, self.ADMIN_EMAIL))
        return admin_list

    def DATABASES(self):
        """
        Defines the database properties

        :return: List of all available databases
        """
        return {
            "default": {
                "ENGINE": self.SQL_BACKEND,
                "NAME": self.SQL_NAME,
                "HOST": self.SQL_SERVER,
                "PORT": self.SQL_PORT,
                "USER": self.SQL_USER,
                "PASSWORD": self.SQL_PASSWORD
            }
        }

    def SERVER_EMAIL(self):
        """
        Defines an e-mail where all errors will come from

        :return: the e-mail where all errors will come from
        """
        return self.DEFAULT_FROM_EMAIL

    def SECURE_SSL_HOST(self):
        """
        All HTTP requests will be redirected to this host

        :return: where all HTTP request shall be redirected
        """
        if len(self.SECURE_SSL_HOSTNAME) > 0:
            return self.SECURE_SSL_HOSTNAME
        else:
            return None

    @classmethod
    def CORE_IS_POSIX(cls):
        """
        Checks the operating system running on the server

        :return: True if the server is running under POSIX operating system
        """
        try:
            import posix
            return True
        except ImportError:
            return False

    @classmethod
    def CORE_IS_SUDO(cls):
        """
        Checks whether the server can run administrative functions

        :return: True if the server can run administrative functions False otherwise
        """
        for filename, access_level in cls.admin_files.items():
            if not os.access(filename, access_level):
                return False
        return True
