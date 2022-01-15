import pytz
from django.utils import timezone

from core.entity.entity_providers.model_providers.authentication_provider import AuthenticationProvider

from .raw_sql_query_reader import RawSqlQueryReader
from .model_emulators import ModelEmulator, time_from_db


class AuthenticationReader(RawSqlQueryReader):
    """
    Reads the authentications from the database
    """

    _entity_provider = AuthenticationProvider()

    _lookup_table_name = "core_authentication"

    _query_debug = False

    def initialize_query_builder(self):
        self.items_builder\
            .add_select_expression("core_authentication.id")\
            .add_select_expression("core_authentication.token_hash")\
            .add_select_expression("core_authentication.expiration_date")\
            .add_select_expression("core_user.id")\
            .add_select_expression("core_user.login")\
            .add_select_expression("core_user.name")\
            .add_select_expression("core_user.surname")\
            .add_data_source("core_authentication")
        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.INNER, "core_user", "ON (core_user.id=core_authentication.user_id)")

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source("core_authentication")

    def create_external_object(self, auth_id, auth_token_hash, auth_expiration_date, user_id, user_login, user_name,
                               user_surname):
        return ModelEmulator(
            id=auth_id,
            token_hash=auth_token_hash,
            expiration_date=time_from_db(auth_expiration_date),
            user=ModelEmulator(
                id=user_id,
                login=user_login,
                name=user_name,
                surname=user_surname
            )
        )
