def access_level_provider():
    return [
        ("full", "Полный доступ", "ru-RU"),
        ("data_full", "Работа с данными", "ru-RU"),
        ("data_add", "Только добавление и обработка данных", "ru-RU"),
        ("data_process", "Только обработка данных", "ru-RU"),
        ("data_view", "Только просмотр данных", "ru-RU"),
        ("no_access", "Доступ закрыт", "ru-RU"),
        ("full", "Full access", "en-GB"),
        ("data_full", "Dealing with data", "en-GB"),
        ("data_add", "Data adding and processing only", "en-GB"),
        ("data_process", "Data processing only", "en-GB"),
        ("data_view", "Viewing the data", "en-GB"),
        ("no_access", "No access", "en-GB"),
        ("add", "Добавление приложения в проект", "ru-RU"),
        ("permission_required", "Добавление приложения в проект (с согласия суперпользователя)", "ru-RU"),
        ("add", "Add application", "en-GB"),
        ("permission_required", "Add application (superuser permission required)", "en-GB"),
    ]