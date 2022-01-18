from core.entity.entity_fields.field_managers.entity_value_manager import EntityValueManager
from core.entity.entity_exceptions import EntityOperationNotPermitted


class RefreshTokenManager(EntityValueManager):
    """
    Manages the refresh token and contains the only function called 'refresh'. Such a function refreshes the
    token and saves all information to the database.

    The main HTTP request is sent by the RemoteApiProvider, not this field. This field just notify the
    AuthorizationToken that access_token has been changed.
    """

    def __str__(self):
        """
        :return: a string representation of the Refresh token.
        """
        if self.entity.state == "creating":
            return "<< THE REFRESH TOKEN IS NOT ISSUED >>"
        else:
            return str(self._field_value)

    def __eq__(self, other):
        """
        Compares two refresh tokens

        :param other: another refresh token to compare to
        :return: True if two refresh tokens are the same, False otherwise
        """
        if isinstance(other, RefreshTokenManager):
            return self._field_value == other._field_value
        else:
            return False

    def refresh(self):
        """
        Refreshes the access token according to the value of the refresh token

        :return: nothing
        """
        if self.entity.state == "creating" or self.entity.state == "deleted":
            raise EntityOperationNotPermitted()
        self.entity._access_token = None
        self.entity._expires_in = None
        self.entity.notify_field_changed("access_token")
        self.entity.notify_field_changed("expires_in")
        self.entity.update()
