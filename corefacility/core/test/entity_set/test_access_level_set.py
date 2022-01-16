from parameterized import parameterized

from .base_test_class import BaseTestClass
from ...entity.entity_sets.access_level_set import AccessLevelSet
from ...models.enums import LevelType


PROJECT_ACCESS_LEVELS = [
    ("full", "Full access", "Полный доступ"),
    ("data_full", "Dealing with data", "Работа с данными"),
    ("data_add", "Data adding and processing only", "Только добавление и обработка данных"),
    ("data_process", "Data processing only", "Только обработка данных"),
    ("data_view", "Viewing the data", "Только просмотр данных"),
    ("no_access", "No access", "Доступ закрыт")
]

APPLICATION_ACCESS_LEVELS = [
    ("add", "Add application", "Добавление приложения в проект"),
    ("permission_required", "Add application (superuser permission required)",
        "Добавление приложения в проект (с согласия суперпользователя)"),
    ("usage", "Application usage", "Использование приложения"),
    ("no_access", "No access", "Доступ закрыт"),
]

LANGUAGE_CODES = [
    ("ru-RU", 2, LevelType.project_level, PROJECT_ACCESS_LEVELS),
    ("en-GB", 1, LevelType.project_level, PROJECT_ACCESS_LEVELS),
    ("ru-RU", 2, LevelType.app_level, APPLICATION_ACCESS_LEVELS),
    ("en-GB", 1, LevelType.app_level, APPLICATION_ACCESS_LEVELS),
]


class TestAccessLevelSet(BaseTestClass):
    """
    Provides access level set testing
    """

    @parameterized.expand(LANGUAGE_CODES)
    def test_default_access_levels(self, lang, lang_index, level_type, expected_level_set):
        with self.settings(LANGUAGE_CODE=lang):
            access_level_set = AccessLevelSet()
            access_level_set.type = level_type
            level_index = 0
            self.assertEquals(len(access_level_set), len(expected_level_set),
                              "Number of default level sets is not correct")
            for access_level in access_level_set:
                self.assertEquals(access_level.alias, expected_level_set[level_index][0],
                                  "Access level aliases are not the same")
                self.assertEquals(access_level.name, expected_level_set[level_index][lang_index],
                                  "Access level aliases are not the same")
                level_index += 1


del BaseTestClass
