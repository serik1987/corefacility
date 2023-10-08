import json
from urllib3 import PoolManager
from datetime import datetime, timedelta
from django.core.files import File
from django.utils.translation import gettext as _
from django.utils.timezone import make_aware
from rest_framework import status

from .....entity.entity import Entity
from .....entity.providers.entity_provider import EntityProvider
from .....exceptions.entity_exceptions import AuthorizationException, EntityNotFoundException
from ... import App
from ...entity import AccountSet


class GoogleProvider(EntityProvider):
    """
    Responsible for exchange of the authorization token to the authorization code
    """

    EXCHANGE_URI = "https://oauth2.googleapis.com/token"
    EMAIL_URI = "https://www.googleapis.com/oauth2/v2/userinfo"

    __poolManager = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__poolManager = PoolManager()

    def load_entity(self, entity: Entity):
        """
        Returns None because authorization token can't be loaded from the Google service, this can be just created there
        """
        pass

    def create_entity(self, entity: Entity):
        """
        Exchanges the authorization code to the authorization token
        :param entity: the entity that must contain the authorization code
        :return: the entity that contains the authorization token, refresh token and expiration time for the
        authorization token
        """
        app = App()

        response = self.__poolManager.request(
            'POST',
            self.EXCHANGE_URI,
            fields={
                'code': entity.code,
                'client_id': app.get_client_id(),
                'client_secret': app.get_client_secret(),
                'redirect_uri': app.get_base_uri(None),
                'grant_type': 'authorization_code'
            }
        )
        if response.status >= status.HTTP_400_BAD_REQUEST:
            raise AuthorizationException("/", _("Invalid client ID or client secret"))
        response_data = json.loads(response.data)
        entity._access_token = response_data['access_token']
        entity._expires_in = make_aware(datetime.now() + timedelta(seconds=response_data['expires_in']))
        if 'refresh_token' in response_data:
            entity._refresh_token = response_data['refresh_token']
        else:
            entity._refresh_token = ""
        entity.notify_field_changed('access_token')
        entity.notify_field_changed('expires_in')
        entity.notify_field_changed('refresh_token')

        response = self.__poolManager.request(
            'GET',
            self.EMAIL_URI,
            headers={
                'Authorization': 'Bearer ' + entity.access_token
            }
        )
        if response.status >= status.HTTP_400_BAD_REQUEST:
            raise AuthorizationException("/", _("Invalid client ID or client secret"))
        user_info = json.loads(response.data)

        try:
            user = AccountSet().get(user_info['email']).user
            token, authentication = app.issue_token(user, True)
            entity._authentication = authentication
            entity._authentication_token = token
            entity.notify_field_changed('authentication')
            entity.notify_field_changed('authentication_token')
        except EntityNotFoundException:
            raise AuthorizationException("/",
                                         _("Your Google account was not attached to the corefacility account. " +
                                           "Please, login using another authorization method and attach your Google " +
                                           "account to the corefacility account"))

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        pass

    def update_entity(self, entity: Entity):
        pass

    def delete_entity(self, entity: Entity):
        pass

    def wrap_entity(self, external_object):
        pass

    def unwrap_entity(self, entity: Entity):
        pass

    def attach_file(self, entity: Entity, name: str, value: File) -> None:
        pass

    def detach_file(self, entity: Entity, name: str) -> None:
        pass
