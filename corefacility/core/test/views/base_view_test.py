import re
from bs4 import BeautifulSoup
from rest_framework import status
from rest_framework.test import APITestCase

from core.entity.user import User
from core.entity.entity_providers.posix_providers.posix_provider import PosixProvider
from core.entity.entry_points.authorizations import AuthorizationModule
from core.generic_views.entity_view_mixin import EntityViewMixin


class BaseViewTest(APITestCase):
    """
    This is the base class for all view tests.
    """

    AUTHORIZATION_TOKEN_PATTERN = re.compile(r'const\s+AUTHORIZATION_TOKEN\s+=\s+[\'"]?(\w+)[\'"]?')

    id_field = "id"
    """ The entity identifier """

    API_VERSION = "v1"
    """ Set the API version to test """

    resource_name = None
    """ The URL path segment between the '/api/{version}/' and '/{resource-id}/' parts. """

    superuser_required = True
    """ True to create the superuser account before all tests. False, otherwise. """

    ordinary_user_required = False
    """ True to create the ordinary user account before all tests. False, otherwise. """

    superuser_token = None
    """ When superuser_required == True this field will be set to the authorization token given to the superuser. """

    ordinary_user_token = None
    """ When ordinary_user_token == """

    @staticmethod
    def create_user_and_token(login, name, surname, is_superuser=True):
        """
        Creates a user and issues token for him

        :param login: user login
        :param name: username
        :param surname: user surname
        :param is_superuser: True if the user is superuser, False otherwise
        :return: authorization token
        """
        user = User(login=login, name=name, surname=surname, is_superuser=is_superuser)
        user.create()
        token = AuthorizationModule.issue_token(user)
        return token

    @classmethod
    def setUpTestData(cls):
        PosixProvider.force_disable = True
        super().setUpTestData()
        if cls.superuser_required:
            cls.superuser_token = cls.create_user_and_token("superuser", "Superuser", "Superuserov", True)
        if cls.ordinary_user_required:
            cls.ordinary_user_token = cls.create_user_and_token("user", "User", "Userov", False)

    def setUp(self):
        super().setUp()
        EntityViewMixin.throttle_classes = []

    def tearDown(self):
        if hasattr(EntityViewMixin, "throttle_classes"):
            del EntityViewMixin.throttle_classes
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        PosixProvider.force_disable = False

    def get_entity_list_path(self):
        """
        Returns path for the entity list requests (POST => creating new entity, GET => returns the entity list)

        :return: the entity list path
        """
        resource_name = self.get_resource()
        return "/api/{version}/{resource_name}/".format(version=self.API_VERSION, resource_name=resource_name)

    def get_resource(self):
        """
        Returns the resource name used in path calculation routines

        :return: value of the 'resource_name' public field
        :except: NotImplementedError if you don't re-implement the 'resource_name' field
        """
        if self.resource_name is None:
            raise NotImplementedError("Please, define the 'resource_name' public property")
        return self.resource_name

    def get_entity_detail_path(self, lookup):
        """
        Returns path for the entity detail requests (GET => get entity info, PUT, PATCH => set entity info,
            DELETE => delete the entity)

        :param: lookup Entity ID or alias
        :return: entity path
        """
        resource_name = self.get_resource()
        return "/api/{version}/{resource_name}/{lookup}/".format(
            version=self.API_VERSION, resource_name=resource_name, lookup=lookup)

    def get_authorization_headers(self, token_id):
        """
        Calculates and returns authorization tokens

        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :return: headers to be substituted to the request.
        """
        if token_id is not None:
            token = getattr(self, token_id + "_token")
            extra = {"HTTP_AUTHORIZATION": "Token " + token}
        else:
            extra = {}
        return extra
