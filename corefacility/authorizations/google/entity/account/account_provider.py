from core.entity.entity_providers.model_providers.external_authorization_account_provider import \
    ExternalAuthorizationAccountProvider
from core.entity.entity_providers.model_providers.user_provider import UserProvider
from authorizations.google.models import Account as AccountModel


class AccountProvider(ExternalAuthorizationAccountProvider):
    """
    Exchanges information between the google's Account entity and the database
    """

    _entity_model = AccountModel

    _lookup_field = "email"

    _model_fields = ["email", "user"]

    _entity_class = "authorizations.google.entity.Account"

    _user_provider = UserProvider()

    def wrap_entity(self, external_object):
        """
        When the entity information is loaded from the external source, some external_object
        is created (e.g., a django.db.models.Model for database entity provider or dict for
        POSIX users provider). The goal of this function is to transform such external object
        to the entity.

        This method is called by the EntityReader and you are also free to call this method
        by the load_entity function.

        The wrap_entity doesn't retrieve all fields correctly. This is the main and only main
        reason why EntityProvider and EntityReader doesn't want to retrieve the same fields it saved
        and why test_object_created_updated_and_loaded_default and test_object_created_and_loaded
        test cases fail with AssertionError. However, you can override this method in the inherited
        class in such a way as it retrieves all the fields correctly.

        :param external_object: the object loaded using such external source
        :return: the entity that wraps the external object
        """
        account = super().wrap_entity(external_object)
        account._user = self._user_provider.wrap_entity(external_object.user)
        return account
