from parameterized import parameterized_class, parameterized

from .entity import EntityTest
from .entity_providers.dump_entity_provider import *
from ..data_providers.field_value_providers import alias_provider, string_provider, boolean_provider
from ...entity.entity_exceptions import EntityFieldInvalid


def user_login_provider():
    return [[[
        "login1", "login2", "login3", "login4", "login5", "login6", "login7", "login8", "login9", "login10"
    ]]]


@parameterized_class([
    {
        "entity_name": DumpUser
    }
])
class TestUser(EntityTest):

    @parameterized.expand(alias_provider(min_length=1, max_length=100))
    def test_login(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._login_init_kwargs(), "login", value, initial_value, exc, stage)

    def test_password_hash(self):
        self._test_password_field("password_hash")

    @parameterized.expand(string_provider(min_length=0, max_length=100))
    def test_name(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._other_init_kwargs(), "name", value, initial_value, exc, stage)

    @parameterized.expand(string_provider(min_length=0, max_length=100))
    def test_surname(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._other_init_kwargs(), "surname", value, initial_value, exc, stage)

    @parameterized.expand(string_provider(min_length=0, max_length=254))
    def test_email(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._other_init_kwargs(), "email", value, initial_value, exc, stage)

    @parameterized.expand(string_provider(min_length=0, max_length=20))
    def test_phone(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._other_init_kwargs(), "phone", value, initial_value, exc, stage)

    @parameterized.expand(boolean_provider())
    def test_is_locked(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._other_init_kwargs(), "is_locked", value, initial_value, exc, stage)

    @parameterized.expand(boolean_provider())
    def test_is_superuser(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._other_init_kwargs(), "is_superuser", value, initial_value, exc, stage)

    def test_is_support(self):
        user = self._create_demo_entity()
        with self.assertRaises(ValueError, msg="The user can be successfully marked as 'is_support'"):
            user.is_support = True
            user.create()

    @parameterized.expand(["unix_group", "home_dir", "groups"])
    def test_other_fields(self, field):
        self._test_read_only_field(field)

    def test_avatar(self):
        self._test_load_default_file("avatar")

    def test_activation_code(self):
        self._test_password_field("activation_code_hash")

    def test_activation_code_expiry_date(self):
        self._test_expiry_date_field("activation_code_expiry_date")

    @parameterized.expand(user_login_provider())
    def test_foreach(self, value_set):
        self._test_foreach("login", value_set)

    @parameterized.expand(user_login_provider())
    def test_slice(self, value_set):
        self._test_slicing("login", value_set)

    @parameterized.expand(user_login_provider())
    def test_indexing(self, value_set):
        self._test_indexing("login", value_set)

    def test_no_login_user(self):
        with self.assertRaises(EntityFieldInvalid, msg="The user with no login has been successfully created"):
            self.entity_name().create()

    def _create_demo_entity(self):
        return self.entity_name(login="sergei.kozhukhov")

    def _update_demo_entity(self, entity):
        entity.name = "Sergei"
        entity.surname = "Kozhukhov"

    def _login_init_kwargs(self):
        return {}

    def _other_init_kwargs(self):
        return {
            "login": "sergei.kozhukhov"
        }


del TestUser
del EntityTest
