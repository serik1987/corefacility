from core import App as CoreApp
from core.authorizations import AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization
from authorizations.cookie import App as CookieAuthorization
from authorizations.mailru import App as MailruAuthorization
from authorizations.google import App as GoogleAuthorization
from core.synchronizations import IhnaSynchronization
from imaging import App as ImagingApp
from roi import App as RoiApp

from core.entity.entry_points.authorizations import AuthorizationModule, AuthorizationsEntryPoint
from core.entity.entry_points.projects import ProjectApp, ProjectsEntryPoint
from core.entity.entry_points.settings import SettingsModule, SettingsEntryPoint
from core.entity.entry_points.synchronizations import SynchronizationModule, SynchronizationsEntryPoint
from imaging.entity.entry_points.processors import ProcessorsEntryPoint, ImagingProcessor

from core.test.data_providers.entity_sets import filter_data_provider


def module_provider():
    return [
        (module_class,)
        for module_class in (
            CoreApp, AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization,
            CookieAuthorization, MailruAuthorization, GoogleAuthorization, IhnaSynchronization,
            ImagingApp, RoiApp
        )
    ]


def entry_point_provider():
    return [
        {
            "entry_point": AuthorizationsEntryPoint,
            "base_module_class": AuthorizationModule,
            "expected_module_list": [
                AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization,
                CookieAuthorization, GoogleAuthorization, MailruAuthorization
            ]
        },
        {
            "entry_point": ProjectsEntryPoint,
            "base_module_class": ProjectApp,
            "expected_module_list": [ImagingApp]
        },
        {
            "entry_point": SettingsEntryPoint,
            "base_module_class": SettingsModule,
            "expected_module_list": []
        },
        {
            "entry_point": SynchronizationsEntryPoint,
            "base_module_class": SynchronizationModule,
            "expected_module_list": [IhnaSynchronization]
        },
        {
            "entry_point": ProcessorsEntryPoint,
            "base_module_class": ImagingProcessor,
            "expected_module_list": [RoiApp]
        }
    ]


def modules_method_provider():
    """
    Provides the data in the following manner: is_enabled, entry_point_class, expected_module_list
    """
    return filter_data_provider(
        (True, False),
        [
            (entry_point_info['entry_point'], entry_point_info['expected_module_list'])
            for entry_point_info in entry_point_provider()
        ]
    )
