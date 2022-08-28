import os
import random
import string
import base64

from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.test import TestCase
from parameterized import parameterized

from core.models import Module, EntryPoint, ExternalAuthorizationSession, User

AUTHORIZATION_MODULE_LIST = ["ihna", "google", "mailru"]


def widget_list_provider():
    return [
        (["core", "authorizations"],  [
            ("standard", None),
            ("ihna", "<div class='auth ihna'></div>"),
            ("google", "<div class='auth google'></div>"),
            ("mailru", "<div class='auth mailru'></div>"),
            ("cookie", None),
            ("password_recovery", None),
            ("auto", None),
        ]),
        (["core", "synchronizations"], [
            ("ihna_employees", None),
        ]),
        (["core", "projects"], [
            ("imaging", None),
        ]),
        (["core", "projects", "imaging", "processors"], [
            ("roi", None),
        ]),
    ]


def module_list_provider():
    return [
        ("standard", "core.authorizations.StandardAuthorization"),
        ("ihna", "authorizations.ihna.App"),
        ("google", "authorizations.google.App"),
        ("mailru", "authorizations.mailru.App"),
        ("cookie", "authorizations.cookie.App"),
        ("password_recovery", "core.authorizations.PasswordRecoveryAuthorization"),
        ("auto", "core.authorizations.AutomaticAuthorization"),
    ]


class TestApplicationProcess(TestCase):

    PASSWORD_LENGTH = 25

    auth_sessions = None
    uuid_list = None

    @classmethod
    def setUpTestData(cls):
        cls.auth_sessions = {}
        cls.session_keys = {}
        user = User(login="sergei.kozhukhov")
        user.save()
        for module in AUTHORIZATION_MODULE_LIST:
            password = cls.generate_random_password()
            password_hash = make_password(password)
            module_app = Module.objects.get(parent_entry_point__alias="authorizations", alias=module)
            session = ExternalAuthorizationSession(
                authorization_module=module_app,
                session_key=password_hash,
                session_key_expiry_date=timezone.now()
            )
            session.save()
            session_key = base64.encodebytes((str(session.id) + ":" + password).encode("utf-8")).decode("utf-8")
            cls.auth_sessions[module] = session_key

            Account = cls.get_account_class(module)
            Account(user=user, email="no-reply@ihna.ru").save()

        cls.uuid_list = {}
        for apps_used in ['imaging', 'roi']:
            cls.uuid_list[apps_used] = Module.objects.get(alias=apps_used).uuid

    @parameterized.expand(widget_list_provider())
    def test_widgets_show(self, route, expected_widget_list):
        app = None
        entry_point = None
        current_route = list(route)
        current_look = "app"
        while len(current_route) > 0:
            route_element = current_route.pop(0)
            if current_look == "app":
                app = Module.objects.get(alias=route_element, parent_entry_point=entry_point)
                current_look = "ep"
            elif current_look == "ep":
                entry_point = EntryPoint.objects.get(alias=route_element, belonging_module=app)
                current_look = "app"
        self.assertEquals(current_look, "app")
        values = Module.objects.filter(parent_entry_point=entry_point).values("alias", "html_code")
        self.assertEquals(len(values), len(expected_widget_list),
                          "Number of modules attached to this entry point is not the same as expected")
        for value in values:
            alias = value['alias']
            html_code = value['html_code']
            expected_widget_found = False
            for expected_alias, expected_widget in expected_widget_list:
                if expected_alias == alias:
                    expected_widget_found = True
                    if html_code is not None and expected_widget is None:
                        self.fail("HTML code for module '%s' does not exist but expected" % alias)
                    if html_code is None and expected_widget is not None:
                        self.fail("HTML code for module '%s' exists but not expected" % alias)
                    if html_code is not None and expected_widget is not None:
                        self.assertHTMLEqual(html_code, expected_widget,
                                             "HTML code for module '%s' is not the same as expected" % html_code)
                    break
            self.assertTrue(expected_widget_found, "the module '%s' is not within the list of expected modules" %
                            alias)

    @parameterized.expand(module_list_provider())
    def test_authorization_modules(self, alias, expected_authorization_module):
        authorization_app = Module.objects.get(parent_entry_point__alias="authorizations", alias=alias)
        authorization_module = authorization_app.app_class
        self.assertEquals(authorization_module, expected_authorization_module)

    def test_authorization_sessions(self):
        for module, session_key in self.auth_sessions.items():
            session_info = base64.decodebytes(session_key.encode("utf-8")).decode("utf-8")
            session_id, session_password = session_info.split(":", 1)
            session = ExternalAuthorizationSession.objects.get(authorization_module__alias=module, id=session_id)
            stored_password_hash = session.session_key
            self.assertTrue(check_password(session_password, stored_password_hash))
            module_class = session.authorization_module.app_class
            session.delete()
            self.assertTrue(module_class.split('.')[1], module)

    def test_find_user(self):
        for module in AUTHORIZATION_MODULE_LIST:
            account_class = self.get_account_class(module)
            account = account_class.objects.get(email="no-reply@ihna.ru")
            self.assertEquals(account.user.login, "sergei.kozhukhov")

    def test_account_contigency(self):
        for module in AUTHORIZATION_MODULE_LIST:
            self.assertEquals(self.get_account_class(module).objects.count(), 1)
        User.objects.get(login="sergei.kozhukhov").delete()
        for module in AUTHORIZATION_MODULE_LIST:
            self.assertEquals(self.get_account_class(module).objects.count(), 0)

    def test_access_by_uuid(self):
        for module_name, uuid in self.uuid_list.items():
            module_class = Module.objects.get(uuid=uuid).app_class
            actual_module_name, module_class = module_class.split('.')
            self.assertEquals(actual_module_name, module_name)
            self.assertEquals(module_class, "App")

    @classmethod
    def generate_random_password(cls):
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        random.seed = (os.urandom(1024))

        return ''.join(random.choice(chars) for i in range(cls.PASSWORD_LENGTH))

    @classmethod
    def get_account_class(cls, module):
        import authorizations
        auth_module = getattr(authorizations, module)
        return auth_module.models.Account
