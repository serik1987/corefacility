from ....models import FailedAuthorizations as FailedAuthorizationsModel

from .model_provider import ModelProvider
from .user_provider import UserProvider


class FailedAuthorizationProvider(ModelProvider):
    """
    Establishes interaction between the FailedAuthorization entity and the FailedAuthorization Django model
    """

    _entity_model = FailedAuthorizationsModel
    """ the entity model is a Django model that immediately stores information about the entity """

    _model_fields = ['auth_time', 'ip']
    """
    Defines fields in the entity object that shall be stored as Django model. The model fields will be applied
    during object create and update operations
    """

    _entity_class = 'ru.ihna.kozhukhov.core_application.entity.failed_authorization.FailedAuthorization'
    """
    Defines the entity class (the string notation)

    Use the string containing the class name, not class object (due to avoid cycling imports)
    """

    _lookup_field = 'id'
    """
    The lookup field is a unique model field that is used by the load_entity to load the entity copy from the
    database
    """

    _user_provider = UserProvider()
    """ Auxiliary provider that helps to recover the user entity from the user ID """

    def unwrap_entity(self, failed_authorization):
        """
        To save the entity to the external source you must transform the data containing in
        the entity from the Entity format to another format suitable for such external source
        (e.g., an instance of django.db.models.Model class for database entity provider,
        keys for useradd/usermod function for UNIX users provider etc.). The purpose of this
        function is to make such a conversion.

        :param failed_authorization: the entity that must be sent to the external data source
        :return: the entity data suitable for that external source
        """
        failed_authorization_source = super().unwrap_entity(failed_authorization)
        failed_authorization_source.user_id = failed_authorization.user.id
        return failed_authorization_source

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
        failed_authorization = super().wrap_entity(external_object)
        failed_authorization._user = self._user_provider.wrap_entity(external_object.user)
        return failed_authorization
