from core.models.enums import LevelType

prj = LevelType.project_level
app = LevelType.app_level


def access_level_provider():
    return [
        ("full", "Полный доступ", "ru-RU", prj),
        ("data_full", "Работа с данными", "ru-RU", prj),
        ("data_add", "Только добавление и обработка данных", "ru-RU", prj),
        ("data_process", "Только обработка данных", "ru-RU", prj),
        ("data_view", "Только просмотр данных", "ru-RU", prj),
        ("no_access", "Доступ закрыт", "ru-RU", prj),
        ("full", "Full access", "en-GB", prj),
        ("data_full", "Dealing with data", "en-GB", prj),
        ("data_add", "Data adding and processing only", "en-GB", prj),
        ("data_process", "Data processing only", "en-GB", prj),
        ("data_view", "Viewing the data", "en-GB", prj),
        ("no_access", "No access", "en-GB", prj),
        ("add", "Добавление приложения в проект", "ru-RU", app),
        ("permission_required", "Добавление приложения в проект (с согласия суперпользователя)", "ru-RU", app),
        ("usage", "Использование приложения", "ru-RU", app),
        ("no_access", "Доступ закрыт", "ru-RU", app),
        ("add", "Add application", "en-GB", app),
        ("permission_required", "Add application (superuser permission required)", "en-GB", app),
        ("usage", "Application usage", "en-GB", app),
        ("no_access", "No access", "en-GB", app),
    ]