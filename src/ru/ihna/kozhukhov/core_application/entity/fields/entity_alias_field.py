import re
from .entity_field import EntityField
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityFieldInvalid


class EntityAliasField(EntityField):
    """
    Provides additional constraints for setting entity aliases: a string containing only latin letters and digits,
    underscores, dashes or dots
    """

    ENTITY_ALIAS_PATTERN = re.compile(r'^[A-Za-z0-9-_.]+$')

    def __init__(self, max_length=None):
        """
        Defines the alias entity.

        :param max_length: maximum length of the entity object
        """
        super().__init__(str, min_length=1, max_length=max_length, description="Entity alias")

    def correct(self, value):
        """
        Provides additional constraints on setting the entity alias

        :param value: the alias value user wants to set
        :return: the alias value that will actually be set
        """
        raw_value = super().correct(value)
        if self.ENTITY_ALIAS_PATTERN.match(raw_value):
            return raw_value
        else:
            raise EntityFieldInvalid("Entity")
