from core.entity.entity_readers.external_authorization_token_reader import ExternalAuthorizationTokenReader
from core.entity.entity_readers.model_emulators import ModelEmulator, time_from_db

from .model_provider import ModelProvider


class AuthorizationTokenReader(ExternalAuthorizationTokenReader):
    """
    Reads information about all saved authorization tokens from the local database and send them to the
    model provider.
    """

    _lookup_table_name = "google_authorizationtoken"

    _entity_provider = ModelProvider()

    _query_debug = False

    def initialize_query_builder(self):
        super().initialize_query_builder()
        self.items_builder\
            .add_select_expression("google_authorizationtoken.access_token")\
            .add_select_expression("google_authorizationtoken.expires_in")\
            .add_select_expression("google_authorizationtoken.refresh_token")

    def create_external_object(self, token_id, authentication_id, user_id, access_token, expires_in, refresh_token):
        return ModelEmulator(
            id=token_id,
            access_token=access_token,
            expires_in=time_from_db(expires_in),
            refresh_token=refresh_token,
            authentication=ModelEmulator(
                id=authentication_id,
                user=ModelEmulator(
                    id=user_id
                )
            )
        )
