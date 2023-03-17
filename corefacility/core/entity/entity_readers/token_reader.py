from .raw_sql_query_reader import RawSqlQueryReader
from .model_emulators import ModelEmulator, ModelEmulatorFileField, time_from_db


class TokenReader(RawSqlQueryReader):
    """
    This is the base class for all readers related to internally-issued tokens (e.g., authentication and cookie
    tokens)
    """

    def initialize_query_builder(self):
        self.items_builder\
            .add_select_expression("%s.id" % self._lookup_table_name)\
            .add_select_expression("%s.token_hash" % self._lookup_table_name)\
            .add_select_expression("%s.expiration_date" % self._lookup_table_name)\
            .add_select_expression("core_user.id")\
            .add_select_expression("core_user.login")\
            .add_select_expression("core_user.name")\
            .add_select_expression("core_user.surname")\
            .add_select_expression("core_user.email")\
            .add_select_expression("core_user.phone")\
            .add_select_expression("core_user.is_locked")\
            .add_select_expression("core_user.is_superuser")\
            .add_select_expression("core_user.is_support")\
            .add_select_expression("core_user.avatar")\
            .add_select_expression("core_user.unix_group")\
            .add_select_expression("core_user.home_dir")\
            .add_data_source(self._lookup_table_name)\
            .add_order_term(self._lookup_table_name + ".id")
        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.INNER, "core_user",
                      "ON (core_user.id=%s.user_id)" % self._lookup_table_name)

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source(self._lookup_table_name)

    def create_external_object(self, auth_id, auth_token_hash, auth_expiration_date, user_id, user_login, user_name,
                               user_surname, user_email, user_phone,
                               user_is_locked, user_is_superuser, user_is_support, user_avatar,
                               unix_group, home_dir):
        return ModelEmulator(
            id=auth_id,
            token_hash=auth_token_hash,
            expiration_date=time_from_db(auth_expiration_date),
            user=ModelEmulator(
                id=user_id,
                login=user_login,
                name=user_name,
                surname=user_surname,
                email=user_email,
                phone=user_phone,
                is_locked=user_is_locked,
                is_superuser=user_is_superuser,
                is_support=user_is_support,
                avatar=ModelEmulatorFileField(name=user_avatar),
                unix_group=unix_group,
                home_dir=home_dir
            )
        )
