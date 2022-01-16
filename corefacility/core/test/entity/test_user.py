from django.core.files.images import ImageFile
from parameterized import parameterized

from core.entity.user import User
from core.entity.entity_sets.user_set import UserSet
from core.entity.entity_fields.field_managers.entity_password_manager import EntityPasswordManager
from core.entity.entity_exceptions import EntityDuplicatedException, EntityFieldInvalid, EntityOperationNotPermitted

from .base_test_class import BaseTestClass
from .entity_field_mixins.expiry_date_mixin import ExpiryDateMixin
from .entity_field_mixins.file_field_mixin import FileFieldMixin
from .entity_field_mixins.password_mixin import PasswordMixin
from .entity_objects.user_object import UserObject
from ..data_providers.field_value_providers import alias_provider, password_provider, string_provider, \
    boolean_provider, image_provider, token_provider, base_expiry_date_provider
from ..entity_set.entity_set_objects.group_set_object import GroupSetObject
from ..entity_set.entity_set_objects.user_set_object import UserSetObject


class TestUser(PasswordMixin, FileFieldMixin, ExpiryDateMixin, BaseTestClass):
    """
    Provides testing for the user class
    """

    INITIAL_STATE_PRECONDITIONS = [
        (0, 1),  # 0
        (0,),  # 1
        (0, 1),  # 2
        (1, 2),  # 3
        (1, 2),  # 4
        (0, 2, 3),  # 5
        (2, 3, 4),  # 6
        (3, 4),  # 7
        (3, 4),  # 8
        (4,)  # 9
    ]

    GROUP_SUPERVISORS = [
        1,  # 0
        3,  # 1
        4,  # 2
        7,  # 3
        7,  # 4
    ]

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

    def test_user_group_preconditions(self):
        self._make_user_group_preconditions()

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

    def test_groups_preconditions(self):
        user_set_object, group_set_object = self._make_user_group_preconditions()
        obj = UserObject()
        obj.create_entity()
        obj.reload_entity()
        self._check_user_group_preconditions(user_set_object, group_set_object)
        for i in range(5):
            self.assertFalse(group_set_object[i] in obj.entity.groups,
                             "When the user is created it was automatically added into the group")

    @parameterized.expand([
        (n, double_add, inexistent_group)
        for n in range(5)
        for double_add in (True, False)
        for inexistent_group in (True, False)
    ])
    def test_group_add(self, n, double_add, inexistent_group):
        user_set_object, group_set_object = self._make_user_group_preconditions()
        obj = UserObject()
        if not inexistent_group:
            obj.create_entity()
        else:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="The group was successfully assigned to the user that is not created"):
                obj.entity.groups.add(group_set_object[n])
            return
        obj.entity.groups.add(group_set_object[n])
        if double_add:
            obj.entity.groups.add(group_set_object[n])
        obj.reload_entity()
        self._check_user_group_preconditions(user_set_object, group_set_object)
        for i in range(5):
            self.assertEquals(group_set_object[i] in obj.entity.groups, i == n,
                              "The user with ID = %d was incorrectly added into the group with ID = %d" %
                              (obj.entity.id, group_set_object[i].id))

    @parameterized.expand([
        (n,)
        for n in range(5)
    ])
    def test_group_remove(self, n):
        user_set_object, group_set_object = self._make_user_group_preconditions()
        obj = UserObject()
        obj.create_entity()
        obj.entity.groups.add(group_set_object[n])
        obj.reload_entity()
        obj.entity.groups.remove(group_set_object[n])
        obj.reload_entity()
        self._check_user_group_preconditions(user_set_object, group_set_object)
        for i in range(5):
            self.assertFalse(group_set_object[i] in obj.entity.groups,
                             "The group with ID = %d is still in the user list "
                             "after its correct removal from the user" % group_set_object[i].id)

    def test_governor_remove(self):
        user_set_object, group_set_object = self._make_user_group_preconditions()
        sample_group = group_set_object[0]
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The group governor was successfully deleted from the group"):
            sample_group.governor.groups.remove(sample_group)

    def test_group_iteration(self):
        user_set_object, group_set_object = self._make_user_group_preconditions()
        for user_index in range(len(user_set_object)):
            user = user_set_object[user_index]
            for actual_group in user.groups:
                self.assertTrue(actual_group in user.groups,
                                "The group iteration gives non-existent group with ID=%d for user ID=%d" %
                                (actual_group.id, user.id))

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

    def _make_user_group_preconditions(self):
        """
        Creates the user group preconditions

        :return: the user group preconditions
        """
        user_set_object = UserSetObject()
        group_set_object = GroupSetObject(user_set_object)
        return user_set_object, group_set_object

    def _check_user_group_preconditions(self, user_set_object, group_set_object):
        """
        Checks whether the initial preconditions for testing the 'group' property were met

        :param user_set_object: an argument created during _make_user_group_preconditions
        :param group_set_object: an argument created during _make_user_group_preconditions
        :return: nothing
        """
        for user_index in range(len(user_set_object)):
            user = user_set_object[user_index]
            group_index_list = self.INITIAL_STATE_PRECONDITIONS[user_index]
            for group_index in range(len(group_set_object)):
                group = group_set_object[group_index]
                self.assertEquals(group in user.groups, group_index in group_index_list,
                                  "Initial preconditions check failed for user ID = %d, group ID = %d" %
                                  (user.id, group.id))
        for group_index in range(len(group_set_object)):
            supervisor_index = self.GROUP_SUPERVISORS[group_index]
            group = group_set_object[group_index]
            expected_supervisor = user_set_object[supervisor_index]
            actual_supervisor = group.governor
            self.assertEquals(actual_supervisor, expected_supervisor,
                              msg="The governor for the group with ID = %d was unexpectedly modified" % group.id)

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
