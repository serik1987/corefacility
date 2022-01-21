from parameterized import parameterized_class

from core.entity.entry_points.authorizations import AuthorizationsEntryPoint, AuthorizationModule
from core.entity.entry_points.projects import ProjectsEntryPoint, ProjectApp
from core.entity.entry_points.settings import SettingsEntryPoint, SettingsModule
from core.entity.entry_points.synchronizations import SynchronizationsEntryPoint, SynchronizationModule
from core.authorizations import AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization, \
    UnixAuthorization
from core.synchronizations import IhnaSynchronization
from core.entity.entity_sets.corefacility_module_set import CorefacilityModuleSet

from authorizations.cookie import App as CookieAuthorization
from authorizations.google import App as GoogleAuthorization
from authorizations.mailru import App as MailruAuthorization
from authorizations.ihna import App as IhnaAuthorization
from imaging import App as ImagingApp
from imaging.entity.entry_points.processors import ProcessorsEntryPoint, ImagingProcessor
from roi import App as RoiApp

from .base_apps_test import BaseAppsTest


def entry_point_provider():
    return [
        {
            "entry_point": AuthorizationsEntryPoint,
            "base_module_class": AuthorizationModule,
            "expected_module_list": [
                AutomaticAuthorization, UnixAuthorization, PasswordRecoveryAuthorization, StandardAuthorization,
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


@parameterized_class(entry_point_provider())
class TestEntryPoint(BaseAppsTest):
    """
    Tests entry points
    """

    entry_point = None
    expected_module_list = None
    base_module_class = None

    def test_singleton(self):
        """
        Checks whether the entry point is singleton
        """
        ep1 = self.entry_point()
        ep2 = self.entry_point()
        self.assertIs(ep1, ep2, "The entry point is not singleton")

    def test_modules_by_entry_point_alias_iteration(self):
        """
        Checks whether modules were correctly retrieved during the iteration
        """
        ep = self.entry_point()
        module_set = CorefacilityModuleSet()
        module_set.entry_point_alias = ep.alias
        expected_module_count = len(module_set)
        actual_module_count = 0
        for actual_module in module_set:
            module_class = actual_module.__class__
            self.assertIn(module_class, self.expected_module_list,
                          msg="Iterations over all modules revealed unexpected module:" + module_class.__name__)
            expected_module = module_class()
            self.assertModule(actual_module, expected_module, "The modules are not the same")
            self.assertIs(actual_module.parent_entry_point, ep,
                          "Iteration over all entry points returned the module not attached to this entry point")
            self.assertEquals(actual_module.state, "loaded", "Unexpected module state")
            self.assertIsInstance(actual_module, self.base_module_class,
                                  "The module is not an instance of the base module class")
            actual_module_count += 1
        self.assertEquals(actual_module_count, expected_module_count,
                          "The module count received from __iter__ is not the same as module count "
                          "received from __len__")

    def test_modules_by_entry_point_alias_len(self):
        """
        Checks whether total module number was correctly retrieved during counting.
        """
        ep = self.entry_point()
        module_set = CorefacilityModuleSet()
        module_set.entry_point_alias = ep.alias
        actual_module_count = len(module_set)
        expected_module_count = len(self.expected_module_list)
        self.assertEquals(actual_module_count, expected_module_count,
                          "Number of modules attached to this entry point is not the same as expected")
