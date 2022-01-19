from datetime import datetime, timedelta
from django.utils import timezone
from random import randrange
from django.core.files import File

from core.entity.entity import Entity
from core.entity.authentication import Authentication
from core.entity.entity_sets.user_set import UserSet
from core.entity.entity_providers.entity_provider import EntityProvider


class MockProvider(EntityProvider):
    """
    Generates random authorization token and attaches the authorization token to the random account for testing
    purpose.
    """

    TOKEN_MAX_VALUE = 99999999
    TOKEN_MIN_VALUE = 10000000

    EXPIRY_TERM = timedelta(milliseconds=300)

    @staticmethod
    def random_token(name: str):
        return "%d === TEST RANDOM %s ===" % (
            randrange(MockProvider.TOKEN_MIN_VALUE, MockProvider.TOKEN_MAX_VALUE),
            name.upper()
        )

    def load_entity(self, entity: Entity):
        pass

    def create_entity(self, entity: Entity):
        """
        Creates the authorization token and updates all entity fields.

        :param entity: the entity to update
        :return: nothing
        """
        self._generate_random_token(entity)
        self._generate_expiration_date(entity)
        self._generate_random_refresh_token(entity)
        self._generate_random_authentication(entity)

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        pass

    def update_entity(self, entity: Entity):
        self._generate_random_token(entity)
        self._generate_expiration_date(entity)

    def delete_entity(self, entity: Entity):
        pass

    def wrap_entity(self, external_object):
        pass

    def unwrap_entity(self, entity: Entity):
        pass

    def attach_file(self, entity: Entity, name: str, value: File) -> None:
        pass

    def detach_file(self, entity: Entity, name: str) -> None:
        pass

    def attach_entity(self, container: Entity, property_name: str, entity: Entity) -> None:
        pass

    def detach_entity(self, container: Entity, property_name: str, entity: Entity) -> None:
        pass

    def _generate_random_token(self, entity: Entity) -> None:
        entity._access_token = self.random_token("access token")
        entity.notify_field_changed("access_token")

    def _generate_expiration_date(self, entity: Entity) -> None:
        expiration_date = datetime.now() + self.EXPIRY_TERM
        entity._expires_in = timezone.make_aware(expiration_date)
        entity.notify_field_changed("expires_in")

    def _generate_random_refresh_token(self, entity: Entity) -> None:
        entity._refresh_token = self.random_token("refresh token")
        entity.notify_field_changed("refresh_token")

    def _generate_random_authentication(self, entity: Entity) -> None:
        user_set = UserSet()
        user_set.is_support = False
        user_number = len(user_set)
        if user_number < 1:
            raise RuntimeError("Please, create at least one user during the setUpTestData")
        user_index = randrange(user_number)
        user = user_set[user_index]
        authentication = Authentication(user=user)
        authentication.token_hash.generate(authentication.token_hash.ALL_SYMBOLS, authentication.TOKEN_PASSWORD_SIZE)
        authentication.expiration_date.set(self.EXPIRY_TERM)
        authentication.create()
        entity._authentication = authentication
        entity.notify_field_changed("authentication")
