from random import randrange
from datetime import datetime, timedelta

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.core.files import File

from core.entity.entity import Entity
from core.entity.entity_sets.user_set import UserSet
from core.entity.authentication import Authentication
from core.entity.entity_providers.entity_provider import EntityProvider
from core.entity.entity_exceptions import EntityDuplicatedException


class MockProvider(EntityProvider):
    """
    For testing purpose only. Will be removed when the AuthorizationToken will be fully developed.
    """

    TOKEN_EXPIRATION_TERM = timedelta(milliseconds=300)
    MAX_TOKEN_NUMBER = 1000

    def load_entity(self, entity: Entity):
        pass

    def create_entity(self, entity: Entity):
        self._generate_access_token(entity)
        self._generate_expiration_term(entity)
        self._generate_refresh_token(entity)
        self._attach_random_user(entity)

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        raise EntityDuplicatedException()

    def update_entity(self, entity: Entity):
        self._generate_access_token(entity)
        self._generate_expiration_term(entity)

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

    def _generate_access_token(self, entity):
        entity._access_token = str(randrange(self.MAX_TOKEN_NUMBER)) + " === DUMP ACCESS TOKEN ==="
        entity.notify_field_changed("access_token")

    def _generate_expiration_term(self, entity):
        entity._expires_in = timezone.make_aware(datetime.now() + self.TOKEN_EXPIRATION_TERM)
        entity.notify_field_changed("expires_in")

    def _generate_refresh_token(self, entity):
        entity._refresh_token = str(randrange(self.MAX_TOKEN_NUMBER)) + " === DUMP REFRESH TOKEN ==="
        entity.notify_field_changed("refresh_token")

    def _attach_random_user(self, entity):
        user_set = UserSet()
        user_set.is_support = False
        user_number = len(user_set)
        if user_number < 1:
            raise ImproperlyConfigured("Please, create at least one test user during the setUpTestData")
        user_index = randrange(user_number)
        user = user_set[user_index]
        auth = Authentication(user=user)
        auth.token_hash.generate(auth.token_hash.ALL_SYMBOLS, auth.TOKEN_PASSWORD_SIZE)
        auth.expiration_date.set(self.TOKEN_EXPIRATION_TERM)
        auth.create()
        entity._authentication = auth
        entity.notify_field_changed("authentication")
