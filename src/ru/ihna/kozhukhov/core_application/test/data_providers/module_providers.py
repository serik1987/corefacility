from ... import App as CoreApp
from ...modules.auth_auto import AutomaticAuthorization
from ...modules.auth_password_recovery import PasswordRecoveryAuthorization
from ...modules.auth_standard import StandardAuthorization
from ...modules.auth_cookie import App as CookieAuthorization
from ...modules.auth_mailru import App as MailruAuthorization
from ...modules.auth_google import App as GoogleAuthorization
from ...modules.sync_ihna_employee import IhnaSynchronization

from ...entry_points.authorizations import AuthorizationModule, AuthorizationsEntryPoint
from ...entry_points.projects import ProjectApp, ProjectsEntryPoint
from ...entry_points.synchronizations import SynchronizationModule, SynchronizationsEntryPoint

from .entity_sets import filter_data_provider


def module_provider():
    return [
        (module_class,)
        for module_class in (
            CoreApp, AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization,
            CookieAuthorization, MailruAuthorization, GoogleAuthorization, IhnaSynchronization,
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
        },
        {
            "entry_point": SynchronizationsEntryPoint,
            "base_module_class": SynchronizationModule,
            "expected_module_list": [IhnaSynchronization]
        },
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
