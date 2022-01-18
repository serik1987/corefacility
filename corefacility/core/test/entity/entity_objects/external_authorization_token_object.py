from random import randrange

from .entity_object import EntityObject


class ExternalAuthorizationTokenObject(EntityObject):
    """
    Facilitates creation of the testing external authorization tokens.
    """

    MAX_AUTHORIZATION_CODE = 1000

    _default_create_kwargs = {
        "code": str(randrange(MAX_AUTHORIZATION_CODE)) + " === DUMP AUTHORIZATION CODE ==="
    }

    def create_entity(self):
        super().create_entity()
        self._entity_fields['code'] = None
        self._entity_fields['authentication'] = self._entity.authentication
