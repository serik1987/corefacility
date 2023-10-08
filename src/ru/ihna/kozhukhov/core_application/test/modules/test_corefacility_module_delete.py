from django.test import TestCase
from parameterized import parameterized

from ... import App as CoreApp
from ...entry_points.projects import ProjectsEntryPoint
from ...exceptions.entity_exceptions import RootModuleDeleteException, EntityNotFoundException
from ...entity.field_managers.module_settings_manager import ModuleSettingsManager
from ...entity.entity_sets.corefacility_module_set import CorefacilityModuleSet
from ...entity.entity_sets.entry_point_set import EntryPointSet

from ...modules.auth_auto import AutomaticAuthorization
from ...modules.auth_password_recovery import PasswordRecoveryAuthorization
from ...modules.auth_standard import StandardAuthorization
from ...modules.auth_cookie import App as CookieAuthorization
from ...modules.auth_mailru import App as MailruAuthorization
from ...modules.auth_google import App as GoogleAuthorization
from ...modules.sync_ihna_employee import IhnaSynchronization


def module_delete_provider():
    return [
        (CoreApp, RootModuleDeleteException),
        (AutomaticAuthorization, None),
        (PasswordRecoveryAuthorization, None),
        (StandardAuthorization, None),
        (CookieAuthorization, None),
        (MailruAuthorization, None),
        (GoogleAuthorization, None),
        (IhnaSynchronization, None),
    ]


class TestCorefacilityModuleDelete(TestCase):

    def setUp(self):

        # Reloading all modules from the database
        module_set = CorefacilityModuleSet()
        for _ in module_set:
            pass

        # Reloading all entry points from the database
        entry_point_set = EntryPointSet()
        for _ in entry_point_set:
            pass

    @classmethod
    def tearDownClass(cls):
        AutomaticAuthorization.reset()
        PasswordRecoveryAuthorization.reset()
        StandardAuthorization.reset()
        CookieAuthorization.reset()
        MailruAuthorization.reset()
        GoogleAuthorization.reset()
        IhnaSynchronization.reset()
        ProjectsEntryPoint.reset()
        super().tearDownClass()

    @parameterized.expand(module_delete_provider())
    def test_delete(self, module_class, expected_exception):
        module = module_class()
        self.assertEquals(module.state, "loaded")
        entry_point = module.parent_entry_point
        alias = module.alias
        if expected_exception is not None:
            with self.assertRaises(expected_exception,
                                   msg="The module constraint (one can't delete the module "
                                       "if no child module was deleted) doesn't work"):
                module.delete()
        else:
            module.delete()
            self.assertIn(module.state, ("deleted", "deprecated"),
                          "The module state doesn't switched to 'deleted' after module delete")
            with self.assertRaises(EntityNotFoundException,
                                   msg="The module has been deleted but still presented in the database"):
                module_set = CorefacilityModuleSet()
                module_set.entry_point = entry_point
                module_set.get(alias)
            del module
            module_class.reset()
            module = module_class()
            self.assertEquals(module.state, "found",
                              "The state of the delete module is not FOUND when the module has been resetted")
            self.assertEquals(module.uuid, "xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx",
                              "The module UUID was not successfully cleared when the module was deleted")
            self.assertIsInstance(module.user_settings, ModuleSettingsManager,
                                  "The module settings must be an instance of ModuleSettingsManager even though "
                                  "the module does not exist")
            self.assertIsNone(module.is_enabled,
                              "The module enability status was not successfully cleared when the module was deleted")
            self.assertEquals(module.state, "uninstalled",
                              "The module status was not turned to UNINSTALLED when autoload properties were accessed")
            module_class.reset()
