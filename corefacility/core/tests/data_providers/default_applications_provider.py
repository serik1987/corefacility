def get_default_applications_provider():
    return {
        "core": {
            "parent_entry_point": None,
            "name_ru": "Базовый функционал",
            "name_en": "Core functionality",
            "html_code": None,
            "is_application": False,
            "is_enabled": True,
            "entry_points": {
                "authorizations": {
                    "name_ru": "Способы авторизации",
                    "name_en": "Authorization methods",
                    "type": "lst",
                    "modules": {
                        "standard": {
                            "name_ru": "Стандартная авторизация",
                            "name_en": "Standard authorization",
                            "html_code": None,
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "ihna": {
                            "parent_entry_point": "authroizations",
                            "name_ru": "Авторизация через сайт ИВНД и НФ РАН",
                            "name_en": "Authorization through IHNA website",
                            "html_code": "<div class='auth ihna'></div>",
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "google": {
                            "parent_entry_point": "authorizations",
                            "name_ru": "Авторизация через Google",
                            "name_en": "Authorization through Google",
                            "html_code": "<div class='auth google'></div>",
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "mailru": {
                            "parent_entry_point": "authorizations",
                            "name_ru": "Авторизация через Mail.ru",
                            "name_en": "Authorization through Mail.ru",
                            "html_code": "<div class='auth mailru'></div>",
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "unix": {
                            "parent_entry_point": "authorizations",
                            "name_ru": "Авторизация через операционную систему",
                            "name_en": "Authorization through UNIX account",
                            "html_code": None,
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "cookie": {
                            "parent_entry_point": "authorizations",
                            "name_ru": "Авторизация через Cookie",
                            "name_en": "Authorization through Cookie",
                            "html_code": None,
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "password_recovery": {
                            "parent_entry_point": "authorizations",
                            "name_ru": "Функция восстановления пароля",
                            "name_en": "Password recovery function",
                            "html_code": None,
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                        "auto": {
                            "parent_entry_point": "authorizations",
                            "name_ru": "Автоматическая авторизация",
                            "name_en": "Automatic authorization",
                            "html_code": None,
                            "is_application": False,
                            "is_enabled": True,
                            "entry_points": {}
                        },
                    }
                },

                "synchronizations": {
                    "name_ru": "Синхронизация учётных записей",
                    "name_en": "Account synchronization",
                    "type": "sel",
                    "modules": {
                        "ihna_employees": {
                            "parent_entry_point": "synchronizations",
                            "name_ru": "Синхронизация с сайтом ИВНД и НФ РАН",
                            "name_en": "IHNA RAS account synchronization",
                            "html_code": None,
                            "is_application": False,
                            "is_enabled": False,
                            "entry_points": {}
                        },
                    }
                },

                "projects": {
                    "name_ru": "Работа с научными проектами",
                    "name_en": "Project applications",
                    "type": "lst",
                    "modules": {
                        "imaging": {
                            "parent_entry_point": "projects",
                            "name_ru": "Базовая обработка функциональных карт",
                            "name_en": "Basic functional maps processing",
                            "html_code": None,
                            "is_application": True,
                            "is_enabled": True,
                            "entry_points": {
                                "processors": {
                                    "name_ru": "Обработка функциональных карт",
                                    "name_en": "Imaging processors",
                                    "type": "lst",
                                    "modules": {
                                        "roi": {
                                            "parent_entry_point": "processors",
                                            "name_ru": "Выделение ROI",
                                            "name_en": "ROI definition",
                                            "html_code": None,
                                            "is_application": True,
                                            "is_enabled": True,
                                            "entry_points": {}
                                        }
                                    }
                                }
                            }
                        },
                    }
                },

                "settings": {
                    "name_ru": "Прочие настройки",
                    "name_en": "Other settings",
                    "type": "lst",
                    "modules": {}
                }
            },
        },
    }
