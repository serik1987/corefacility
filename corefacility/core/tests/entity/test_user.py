import warnings

from django.core.files.images import ImageFile
from parameterized import parameterized

from .base_test_class import BaseTestClass
from .entity_field_mixins.expiry_date_mixin import ExpiryDateMixin
from .entity_field_mixins.file_field_mixin import FileFieldMixin
from .entity_field_mixins.password_mixin import PasswordMixin
from .entity_objects.user_object import UserObject
from ..data_providers.field_value_providers import alias_provider, password_provider, string_provider, boolean_provider, \
    image_provider, token_provider, base_expiry_date_provider
from ...entity.entity_exceptions import EntityDuplicatedException, EntityFieldInvalid
from ...entity.entity_fields import EntityPasswordManager
from ...entity.entity_sets.user_set import UserSet
from ...entity.user import User


class TestUser(PasswordMixin, FileFieldMixin, ExpiryDateMixin, BaseTestClass):
    """
    Provides testing for the user class
    """

    _entity_object_class = UserObject
    """ The entity object class. New entity object will be created from this class """

    @parameterized.expand(alias_provider(1, 100))
    def test_login(self, *args):
        """
        Provides user login test

        :param login: login during the user create
        :param another_login: login during the user field change
        :param throwing_exception: None for positive test, exception than shall be thrown for negative tests
        :param test_number: the test number to be used in the _test_field
        :return: nothing
        """
        self._test_field("login", *args, use_defaults=False)

    def test_login_uniqueness(self):
        user1 = User(login="sergei.kozhukhov")
        user1.create()
        user2 = User(login="sergei.kozhukhov")
        with self.assertRaises(EntityDuplicatedException,
                               msg="Two users with the same login were created (negative test failed)"):
            user2.create()

    @parameterized.expand(password_provider())
    def test_password(self, *args):
        self._test_password("password_hash", *args)

    @parameterized.expand(string_provider(0, 100))
    def test_name(self, *args):
        self._test_field("name", *args)

    @parameterized.expand(string_provider(0, 100))
    def test_surname(self, *args):
        self._test_field("surname", *args)

    @parameterized.expand(string_provider(0, 254))
    def test_email(self, *args):
        self._test_field("email", *args)

    @parameterized.expand(string_provider(0, 20))
    def test_phone(self, *args):
        self._test_field("phone", *args)

    def test_user_groups(self):
        warnings.warn("TO-DO: test groups where user exists (group sets development required)")

    @parameterized.expand(boolean_provider())
    def test_is_locked(self, *args):
        self._test_field("is_locked", *args)

    @parameterized.expand(boolean_provider())
    def test_is_superuser(self, *args):
        self._test_field("is_superuser", *args)

    def test_is_support(self):
        self._test_read_only_field("is_support", True)

    @parameterized.expand(image_provider())
    def test_avatar(self, filename, throwing_exception, test_number):
        self._test_file_field("avatar", "/static/core/user.svg", ImageFile,
                              filename, throwing_exception, test_number)

    def test_unix_group(self):
        self._test_read_only_field("unix_group", "root")

    def test_home_dir(self):
        self._test_read_only_field("home_dir", "/var/log")

    @parameterized.expand(token_provider())
    def test_activation_code(self, *args):
        self._test_password("activation_code_hash", *args)

    @parameterized.expand(base_expiry_date_provider())
    def test_activation_code_expiry_date(self, *args):
        self._test_expiry_date("activation_code_expiry_date", *args)

    def test_support_update(self):
        support = UserSet().get("support")
        support.password_hash.generate(EntityPasswordManager.SMALL_LATIN_LETTERS, 3)
        with self.assertRaises(EntityFieldInvalid, msg="the password for support user can be set"):
            support.update()

    def test_support_user_delete(self):
        support = UserSet().get("support")
        with self.assertRaises(EntityFieldInvalid, msg="The support user can be deleted"):
            support.delete()

    def test_support_user_login(self):
        support = UserSet().get("support")
        self.assertTrue(support.password_hash.check("support"),
                        msg="The support user password was not set to 'support'")

    def test_support_user_lock(self):
        support = UserSet().get("support")
        support.is_locked = True
        support.update()
        support = UserSet().get("support")
        self.assertTrue(support.is_locked, "The support user can't be properly locked")

    def test_support_user_unlock(self):
        support = UserSet().get("support")
        support.is_locked = False
        support.update()
        support = UserSet().get("support")
        self.assertFalse(support.is_locked, "The support user can't be properly unlocked")

    def _check_default_fields(self, user):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param user: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(user.login, "sergei.kozhukhov", "The user login was unexpectedly changed")
        self._check_empty_fields(user)

    def _check_default_change(self, user):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param user: the entity to store
        :return: nothing
        """
        self.assertEquals(user.login, "ivan.ivanov", "The user login doesn't changed or improperly changed")
        self._check_empty_fields(user)

    def _check_empty_fields(self, user):
        """
        Checks fields that are not modified during the user create or change by means of the user object

        :param user: the entity which default fields shall be checked
        :return:
        """
        self.assertIsNot(user.name, "The user name was unexpectedly changed")
        self.assertIsNone(user.surname, "The user surname was unexpectedly changed")
        self.assertIsNone(user.email, "The user E-mail was unexpectedly changed")
        self.assertIsNone(user.phone, "The user phone number was unexpectedly changed")
        self.assertFalse(user.is_locked, "The user locking status was unexpectedly changed")
        self.assertFalse(user.is_superuser, "The user's superuser status was unexpectedly changed")
        self.assertFalse(user.is_support, "The user support status was unexpectedly changed")
        self.assertEquals(user.avatar.url, "/static/core/user.svg",
                          "The user default avatar did not set")
        self.assertIsNone(user.unix_group, "The default user unix group was changed")
        self.assertIsNone(user.home_dir, "The default user home directory was changed")


del BaseTestClass
