from core.entity.entity_fields.field_managers.entity_value_manager import EntityValueManager


class RefreshTokenManager(EntityValueManager):
    """
    Manages refresh tokens
    """

    def refresh(self):
        self.entity._access_token = None
        self.entity._expires_in = None
        self.entity.notify_field_changed("access_token")
        self.entity.notify_field_changed("expires_in")
        self.entity.update()

    def __str__(self):
        return self._field_value

    def __eq__(self, other):
        if isinstance(other, RefreshTokenManager):
            return self._field_value == other._field_value
        else:
            return False
