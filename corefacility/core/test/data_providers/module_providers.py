from core import App as CoreApp
from core.authorizations import AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization
from authorizations.cookie import App as CookieAuthorization
from authorizations.ihna import App as IhnaAuthorization
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


def module_provider():
    return [
        (module_class,)
        for module_class in (
            CoreApp, AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization,
            CookieAuthorization, IhnaAuthorization, MailruAuthorization, GoogleAuthorization, IhnaSynchronization,
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
                CookieAuthorization, GoogleAuthorization, MailruAuthorization, IhnaAuthorization
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
