from parameterized import parameterized

from core.models.enums import LevelType

from .base_test_class import BaseTestClass
from .entity_objects.access_level_object import AccessLevelObject
from ..data_providers.field_value_providers import alias_provider, string_provider


class TestAccessLevel(BaseTestClass):
    """
    Checks whether access levels work correctly
    """

    _entity_object_class = AccessLevelObject

    @parameterized.expand([LevelType.project_level, "some unknown level"])
    def test_level_type(self, level_type):
        self._test_read_only_field("type", level_type)

    @parameterized.expand(alias_provider(1, 50))
    def test_alias(self, *args):
        self._test_field("alias", *args, use_defaults=False, name="Тестовый доступ")

    @parameterized.expand(string_provider(1, 64))
    def test_name(self, *args):
        self._test_field("name", *args, use_defaults=True, alias="test_access")

    def _check_default_fields(self, entity):
        self.assertEquals(entity.type, LevelType.app_level, "The access level type is not retrieved successfully")
        self.assertEquals(entity.alias, "sim", "The access level alias is not retrieved successfully")
        self.assertEquals(entity.name, "Launching simulation", "The access level name was not retrieved successfully")

    def _check_default_change(self, entity):
        self.assertEquals(entity.type, LevelType.app_level, "The access level type is not retrieved successfully")
        self.assertEquals(entity.alias, "sim", "The access level alias is not retrieved successfully")
        self.assertEquals(entity.name, "Running simulation", "The access level name was not retrieved successfully")


del BaseTestClass
