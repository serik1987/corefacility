from parameterized import parameterized

from .base_test_class import BaseTestClass
from .entity_objects.access_level_object import AccessLevelObject
from ..data_providers.field_value_providers import alias_provider, string_provider
from ru.ihna.kozhukhov.core_application.entity.access_level import AccessLevel
from ...exceptions.entity_exceptions import EntityOperationNotPermitted
from ru.ihna.kozhukhov.core_application.entity.entity_sets.access_level_set import AccessLevelSet


class TestAccessLevel(BaseTestClass):
    """
    Checks whether access levels work correctly
    """

    _entity_object_class = AccessLevelObject

    @parameterized.expand(alias_provider(1, 50))
    def test_alias(self, *args):
        self._test_field("alias", *args, use_defaults=False, name="Тестовый доступ")

    @parameterized.expand(string_provider(1, 64))
    def test_name(self, *args):
        self._test_field("name", *args, use_defaults=True, alias="test_access")

    def test_project_level_create(self):
        with self.assertRaises(ValueError, msg="The project access level was created"):
            AccessLevel(alias="test", name="Test access")

    def test_standard_access_level_change(self):
        level_set = AccessLevelSet()
        for level in level_set:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The standard access level was successfully changed"):
                level.alias = "bad_alias"
                level.update()

    def test_standard_access_level_delete(self):
        level_set = AccessLevelSet()
        for level in level_set:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The standard access level was successfully deleted"):
                level.delete()

    def _check_default_fields(self, entity):
        self.assertEquals(entity.alias, "sim", "The access level alias is not retrieved successfully")
        self.assertEquals(entity.name, "Launching simulation", "The access level name was not retrieved successfully")

    def _check_default_change(self, entity):
        self.assertEquals(entity.alias, "sim", "The access level alias is not retrieved successfully")
        self.assertEquals(entity.name, "Running simulation", "The access level name was not retrieved successfully")


del BaseTestClass
