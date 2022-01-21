from django.test import TestCase
from parameterized import parameterized_class

from core import App as CoreApp
from core.authorizations import AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization, \
    UnixAuthorization
from core.entity.entity_sets.corefacility_module_set import CorefacilityModuleSet
from authorizations.cookie import App as CookieAuthorization
from authorizations.ihna import App as IhnaAuthorization
from authorizations.mailru import App as MailruAuthorization
from authorizations.google import App as GoogleAuthorization
from core.synchronizations import IhnaSynchronization
from imaging import App as ImagingApp
from roi import App as RoiApp


def module_provider():
    return [
        {"module_class": module_class}
        for module_class in (
            CoreApp, AutomaticAuthorization, PasswordRecoveryAuthorization, StandardAuthorization, UnixAuthorization,
            CookieAuthorization, IhnaAuthorization, MailruAuthorization, GoogleAuthorization, IhnaSynchronization,
            ImagingApp, RoiApp
        )
    ]


@parameterized_class(module_provider())
class TestCorefacilityModule(TestCase):
    """
    Provides basic testing all corefacility modules as applications
    """

    module_class = None

    def test_singleton(self):
        """
        Tests whether the module is singleton
        """
        module1 = self.module_class()
        module2 = self.module_class()
        self.assertIs(module1, module2, "The module %s  doesn't have singleton properties" % str(self.module_class))
