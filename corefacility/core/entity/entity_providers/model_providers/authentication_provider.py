from core.models import Authentication as AuthenticationModel

from .model_provider import ModelProvider
from .user_provider import UserProvider


class AuthenticationProvider(ModelProvider):
    """
    Launches the authentication provider.
    """

    _entity_class = "core.entity.authentication.Authentication"
    _entity_model = AuthenticationModel
    _lookup_field = "id"
    _model_fields = ["id", "token_hash", "expiration_date", "user"]
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
        authentication = super().wrap_entity(external_object)
        authentication._user = self._user_provider.wrap_entity(external_object.user)
        return authentication
