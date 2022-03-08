from parameterized import parameterized

from core import models
from core.models.enums import LevelType
from core.entity.group import Group
from core.entity.project_application import ProjectApplication
from core.entity.access_level import AccessLevelSet
from core.entity.entity_exceptions import EntityOperationNotPermitted
from core.entity.corefacility_module import CorefacilityModuleSet
from imaging import App as ImagingApp
from roi import App as RoiApp

from core.test.data_providers.entity_sets import filter_data_provider
from .base_permissions_test import BasePermissionsTest


def initial_access_level_scheme_provider():
    return [
        (RoiApp, 0, "add", None),
        (RoiApp, 1, "permission_required", None),
        (RoiApp, 2, "usage", None),
        (RoiApp, 3, "no_access", None),
        (RoiApp, 4, "add", None),
        (RoiApp, -1, None, None),
        (RoiApp, Group(), None, EntityOperationNotPermitted),

        (ImagingApp, 0, "permission_required", None),
        (ImagingApp, 1, "usage", None),
        (ImagingApp, 2, "no_access", None),
        (ImagingApp, 3, "add", None),
        (ImagingApp, 4, "permission_required", None),
        (ImagingApp, -1, None, None),
        (ImagingApp, Group(), None, EntityOperationNotPermitted),
    ]


def group_set_provider():
    return [
        (RoiApp, 3, "add", False, True, True),
        (RoiApp, 3, "permission_required", False, True, True),
        (RoiApp, -1, "usage", True, True, True),
        (RoiApp, Group(), "add", False, False, False),

        (ImagingApp, 3, "permission_required", False, True, True),
        (ImagingApp, 3, "usage", False, True, True),
        (ImagingApp, -1, "add", True, True, True),
        (ImagingApp, Group(), "no_access", False, False, False),
    ]


def app_class_provider():
    return [
        (ImagingApp,),
        (RoiApp,),
    ]


def access_level_provider():
    return [
        (0, [
            (RoiApp, False, "add,permission_required"),
            (ImagingApp, False, "permission_required,usage"),
        ]),
        (1, [
            (RoiApp, False, "add"),
            (ImagingApp, False, "permission_required"),
        ]),
        (2, [
            (RoiApp, False, "add,permission_required"),
            (ImagingApp, False, "permission_required,usage"),
        ]),
        (3, [
            (RoiApp, False, "permission_required,usage"),
            (ImagingApp, False, "usage,no_access"),
        ]),
        (4, [
            (RoiApp, False, "permission_required,usage"),
            (ImagingApp, False, "usage,no_access"),
        ]),
        (5, [
            (RoiApp, False, "add,usage,no_access"),
            (ImagingApp, False, "permission_required,no_access,add"),
        ]),
        (6, [
            (RoiApp, False, "usage,no_access,add"),
            (ImagingApp, False, "no_access,add,permission_required"),
        ]),
        (7, [
            (RoiApp, False, "no_access,add"),
            (ImagingApp, False, "add,permission_required"),
        ]),
        (8, [
            (RoiApp, False, "no_access,add"),
            (ImagingApp, False, "add,permission_required"),
        ]),
        (9, [
            (RoiApp, False, "add"),
            (ImagingApp, False, "permission_required")
        ])
    ]


def access_level_retrieve_provider():
    return filter_data_provider(
        range(10),
        [
            ("uuid",),
        ]
    )


class TestAppPermissions(BasePermissionsTest):

    permission_model = models.AppPermission

    entity_field = "application_id"

    entity_set_class = CorefacilityModuleSet

    entity_id_field = "uuid"

    governor_exists = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.set_initial_project_links()
        cls.establish_connections()

    @classmethod
    def set_initial_project_links(cls):
        cls.link_to_project(6, ImagingApp, True)
        cls.link_to_project(6, RoiApp, False)
        cls.link_to_project(7, RoiApp, True)
        cls.link_to_project(7, ImagingApp, False)
        cls.link_to_project(8, RoiApp, True)
        cls.link_to_project(9, ImagingApp, False)
        cls.link_to_project(1, ImagingApp, False)
        cls.link_to_project(1, RoiApp, True)
        cls.link_to_project(2, RoiApp, False)
        cls.link_to_project(2, ImagingApp, True)
        cls.link_to_project(3, ImagingApp, False)
        cls.link_to_project(4, RoiApp, True)

    @classmethod
    def link_to_project(cls, project_index, app_class, is_enabled):
        project = cls._project_set_object[project_index]
        app = app_class()
        project_app = ProjectApplication(project=project, application=app, is_enabled=is_enabled)
        project_app.create()

    @classmethod
    def establish_connections(cls):
        imaging = ImagingApp()
        roi = RoiApp()

        wright = cls._group_set_object[0]
        peculiar = cls._group_set_object[1]
        chaos = cls._group_set_object[2]
        flatter = cls._group_set_object[3]
        revolution = cls._group_set_object[4]

        level_set = AccessLevelSet()
        add = level_set.application_level("add")
        permission_required = level_set.application_level("permission_required")
        usage = level_set.application_level("usage")
        no_access = level_set.application_level("no_access")

        roi.permissions.set(wright, add)
        imaging.permissions.set(wright, permission_required)

        roi.permissions.set(peculiar, permission_required)
        imaging.permissions.set(peculiar, usage)

        roi.permissions.set(chaos, usage)
        imaging.permissions.set(chaos, no_access)

        roi.permissions.set(flatter, no_access)
        imaging.permissions.set(flatter, add)

        roi.permissions.set(revolution, add)
        imaging.permissions.set(revolution, permission_required)

    def setUp(self):
        super().setUp()
        self.level_set = AccessLevelSet()
        self.level_set.type = LevelType.app_level

    @parameterized.expand(initial_access_level_scheme_provider())
    def test_get_permission(self, application_index, group_index, expected_access_level, expected_exception):
        super().test_get_permission(application_index, group_index, expected_access_level, expected_exception)

    @parameterized.expand(group_set_provider())
    def test_set_permission(self, app_class, group_index, access_level, state_must_change,
                            is_deletable, is_settable):
        super().test_set_permission(app_class, group_index, access_level, state_must_change, is_deletable,
                                    is_settable)

    @parameterized.expand(group_set_provider())
    def test_delete_permission(self, app_class, group_index, access_level, state_must_change,
                               is_deletable, is_settable):
        super().test_delete_permission(app_class, group_index, access_level, state_must_change, is_deletable,
                                       is_settable)

    @parameterized.expand(app_class_provider())
    def test_permission_iteration(self, app_class):
        super().test_permission_iteration(app_class, False)

    @parameterized.expand(app_class_provider())
    def test_permission_one_request_iteration(self, app_class):
        super().test_permission_one_request_iteration(app_class)

    @parameterized.expand(access_level_provider())
    def test_entity_iteration_positive(self, user_index, project_info):
        super().test_entity_iteration_positive(user_index, project_info, False)

    @parameterized.expand(access_level_provider())
    def test_entity_iteration_performance(self, user_index, entity_info):
        super().test_entity_iteration_performance(user_index, entity_info)

    @parameterized.expand(access_level_provider())
    def test_entity_len(self, user_index, entity_info):
        super().test_entity_len(user_index, entity_info)

    @parameterized.expand(access_level_retrieve_provider())
    def test_entity_retrieve(self, user_index, lookup_field):
        super().test_entity_retrieve(user_index, lookup_field)

    def get_entity_by_index(self, app_class):
        return app_class()

    def get_incorrect_access_level(self):
        level_set = AccessLevelSet()
        level_set.type = LevelType.project_level
        return level_set.get("full")

    def get_entity_list(self, app_info):
        return [
            (app_class(), is_governor, access_control_list)
            for app_class, is_governor, access_control_list in app_info
        ]

    def assertEntityEquals(self, actual, expected, msg):
        self.assertIs(actual, expected, msg)
        self.assertEquals(actual.state, "loaded", msg + ". Status of the found application is not LOADED")


del BasePermissionsTest
