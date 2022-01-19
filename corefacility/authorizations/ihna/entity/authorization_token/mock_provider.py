from random import randrange
from datetime import timedelta

from django.core.files import File

from core.entity.entity import Entity
from core.entity.authentication import Authentication
from core.entity.entity_sets.user_set import UserSet
from core.entity.entity_providers.entity_provider import EntityProvider


class MockProvider(EntityProvider):
    """
    Receives dump authorization token for testing purpose.
    """

    MIN_CODE_VALUE = 10000000
    MAX_CODE_VALUE = 99999999

    EXPIRY_TERM = timedelta(milliseconds=300)

    @staticmethod
    def generate_mock_code(code_name: str) -> str:
        """
        Generates the random tokens or codes for testing purpose

        :param code_name: name of the generated entity
        :return: the generated value
        """
        return "%d === RANDOM %s FOR TESTING PURPOSE ===" % (
            randrange(MockProvider.MIN_CODE_VALUE, MockProvider.MAX_CODE_VALUE),
            code_name.upper()
        )

    def load_entity(self, entity: Entity):
        pass

    def create_entity(self, entity: Entity):
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

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        pass

    def update_entity(self, entity: Entity):
        pass

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
