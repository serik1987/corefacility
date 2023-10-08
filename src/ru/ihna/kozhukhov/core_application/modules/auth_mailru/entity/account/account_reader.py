from .....entity.readers.external_authorization_account_reader import ExternalAuthorizationAccountReader
from .....entity.readers.model_emulators import ModelEmulator

from .account_provider import AccountProvider


class AccountReader(ExternalAuthorizationAccountReader):
    """
    Reads the account object from the database and organizes it in highly structured manner
    """

    _entity_provider = AccountProvider()

    _lookup_table_name = "auth_mailru_account"

    def initialize_query_builder(self):
        super().initialize_query_builder()
        self.items_builder.add_select_expression("auth_mailru_account.email")

    def create_external_object(self, account_id, user_id, user_login, user_name, user_surname,
                               user_email, user_phone, user_is_locked, user_is_superuser, account_email):
        return ModelEmulator(
            id=account_id,
            email=account_email,
            user=ModelEmulator(
                id=user_id,
                login=user_login,
                name=user_name,
                surname=user_surname,
                email=user_email,
                phone=user_phone,
                is_locked=user_is_locked,
                is_superuser=user_is_superuser
            )
        )
