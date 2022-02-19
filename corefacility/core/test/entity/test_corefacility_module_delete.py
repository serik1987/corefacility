import warnings
from uuid import UUID

from django.test import TestCase
from parameterized import parameterized

from core import App as CoreApp
from core.entity.entity_exceptions import RootModuleDeleteException, ModuleConstraintFailedException, \
    EntityNotFoundException, EntityOperationNotPermitted, ModuleInstallationStateException, \
    ParentModuleNotInstalledException
from core.entity.entity_fields.field_managers.module_settings_manager import ModuleSettingsManager
from core.entity.entity_sets.corefacility_module_set import CorefacilityModuleSet
from core.entity.entry_points.entry_point_set import EntryPointSet
from core.authorizations import AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization, \
    UnixAuthorization

from authorizations.cookie import App as CookieAuthorization
from authorizations.ihna import App as IhnaAuthorization
from authorizations.mailru import App as MailruAuthorization
from authorizations.google import App as GoogleAuthorization
from core.synchronizations import IhnaSynchronization
from imaging import App as ImagingApp
from roi import App as RoiApp


def module_delete_provider():
    return [
        (CoreApp, RootModuleDeleteException),
        (AutomaticAuthorization, None),
        (PasswordRecoveryAuthorization, None),
        (StandardAuthorization, None),
        (UnixAuthorization, None),
        (CookieAuthorization, None),
        (IhnaAuthorization, None),
        (MailruAuthorization, None),
        (GoogleAuthorization, None),
        (IhnaSynchronization, None),
        (ImagingApp, ModuleConstraintFailedException),
        (RoiApp, None)
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
            self.assertEquals(module.state, "deleted",
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

    def test_delete_cascade(self):
        RoiApp.reset()
        ImagingApp.reset()
        roi_app = RoiApp()
        imaging_app = ImagingApp()
        entry_point = imaging_app.get_entry_points()['processors']
        ep_id = entry_point.id
        self.assertEquals(roi_app.state, "found",
                          "The newly initialized module has not the FOUND state")
        roi_app.delete()
        self.assertEquals(imaging_app.state, "found",
                          "The newly initialized module has not the FOUND state")
        imaging_app.delete()
        self.assertEquals(entry_point.state, "deleted",
                          "The entry point was not deleted when belonging module has been deleted")
        ep_set = EntryPointSet()
        with self.assertRaises(EntityNotFoundException,
                               msg="The entry point has not been removed from the database "
                                   "when its parent module was deleted"):
            ep_set.get(ep_id)

    def test_delete_double(self):
        roi_app = RoiApp()
        roi_app.delete()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The same entity can be deleted twice"):
            roi_app.delete()
        RoiApp.reset()
        ImagingApp.reset()

    def test_module_install(self):
        RoiApp().delete()
        ImagingApp().delete()
        RoiApp.reset()
        ImagingApp.reset()
        for module_class in (ImagingApp,):  # TO-DO: also install the RoiApp
            module = module_class()
            module.install()
            with self.assertNumQueries(0):
                self.assertEquals(module.state, "loaded", "The module state must be LOADED after module installation")
                self.assertIsInstance(module.uuid, UUID, "The module UUID must be pre-loaded after installation")
                self.assertEquals(module.alias, module.get_alias(), "The module alias must be reproduced successfully")
                self.assertEquals(len(module.user_settings), 0, "The module's user settings must be empty")
                self.assertEquals(module.is_enabled, True, "The module shall be enabled by default")

    def test_module_double_install(self):
        RoiApp.reset()
        roi_app = RoiApp()
        with self.assertRaises(ModuleInstallationStateException,
                               msg="The pre-installed module can be installed again"):
            roi_app.install()

    def test_module_install_wo_entry_point(self):
        RoiApp().delete()
        ImagingApp().delete()
        RoiApp.reset()
        ImagingApp.reset()
        with self.assertRaises(ParentModuleNotInstalledException,
                               msg="The module can't be installed without parent module being installed"):
            RoiApp().install()
