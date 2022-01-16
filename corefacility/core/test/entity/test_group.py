import warnings

from django.test import TestCase
from parameterized import parameterized

from core.entity.entity_exceptions import EntityFieldInvalid, EntityOperationNotPermitted, GroupGovernorConstraintFails, \
    EntityNotFoundException
from core.entity.entity_sets.user_set import UserSet
from core.entity.group import Group
from core.entity.user import User
from core.models import GroupUser
from core.test.data_providers.field_value_providers import string_provider
from core.test.entity.base_test_class import BaseTestClass
from core.test.entity.entity_objects.group_object import GroupObject


class TestGroup(BaseTestClass):
    """
    Provides regression test of a single scientific group.
    """

    _entity_object_class = GroupObject
    """ The entity object class. New entity object will be created from this class """

    __test_user = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.__test_user = User(login="sergei.kozhukhov", name="Сергей", surname="Кожухов")
        cls.__test_user.create()
        GroupObject.define_default_kwarg("governor", cls.__test_user)

    @parameterized.expand(string_provider(1, 256))
    def test_group_name(self, *args):
        self._test_field("name", *args, use_defaults=False, governor=self.__test_user)

    def test_group_name_required(self):
        group = Group(governor=self.__test_user)
        with self.assertRaises(EntityFieldInvalid, msg="The group with no group name was successfully created"):
            group.create()

    def test_group_governor_positive(self):
        obj = GroupObject()
        obj.create_entity()
        old_governor = obj.entity.governor
        user = User(login="vanya.petrov")
        user.create()
        obj.entity.users.add(user)
        obj.reload_entity()
        user = UserSet().get("vanya.petrov")
        obj.entity.governor = user
        obj.entity.update()
        obj.reload_entity()
        self.assertTrue(obj.entity.users.exists(old_governor),
                        "The old group governor was unexpectedly excluded from the group after reassignment")
        self.assertEquals(obj.entity.governor, user,
                          "The group governor was not loaded properly after its reassignment")

    def test_group_governor_not_in_group(self):
        obj = GroupObject()
        obj.create_entity()
        obj.reload_entity()
        new_user = User(login="vanya.petrov")
        new_user.create()
        with self.assertRaises(EntityFieldInvalid,
                               msg="The user which is not a group member was successfully made as group governor"):
            obj.entity.governor = new_user
            obj.entity.update()

    @parameterized.expand([
        (User(login="vanya.petrov"),),
        ("This is a string, not a user",),
        (None,),
    ])
    def test_group_governor_negative(self, inexistent_governor):
        obj = GroupObject()
        obj.create_entity()
        obj.reload_entity()
        with self.assertRaises(ValueError, msg="An attempt to assign non-existent user is not failed"):
            obj.entity.governor = inexistent_governor

    def test_group_user_not_exists(self):
        obj, new_user = self._create_test_group_users_precondition()
        self._check_test_group_users_preconditions(obj)
        self.assertFalse(obj.entity.users.exists(new_user),
                         "The newly created user is automatically added into the group")

    def test_group_user_add(self):
        obj, new_user = self._create_test_group_users_precondition()
        obj.entity.users.add(new_user)
        obj.reload_entity()
        self._check_test_group_users_preconditions(obj)
        self.assertTrue(obj.entity.users.exists(new_user),
                        "The user was not added into the group")

    def test_group_user_double_add(self):
        obj, new_user = self._create_test_group_users_precondition()
        obj.entity.users.add(new_user)
        obj.entity.users.add(new_user)
        obj.reload_entity()
        self._check_test_group_users_preconditions(obj)
        self.assertTrue(obj.entity.users.exists(new_user),
                        "The user was not added into the group")

    def test_group_user_remove(self):
        obj, new_user = self._create_test_group_users_precondition()
        obj.entity.users.add(new_user)
        obj.entity.users.remove(new_user)
        obj.reload_entity()
        self._check_test_group_users_preconditions(obj)
        self.assertFalse(obj.entity.users.exists(new_user),
                         "Unable to remove user from the group")

    def test_group_user_remove_non_trivial(self):
        obj, new_user = self._create_test_group_users_precondition()
        user_id = new_user.id
        obj.entity.users.add(new_user)
        new_user.delete()
        obj.reload_entity()
        self._check_test_group_users_preconditions(obj)
        with self.assertRaises(GroupUser.DoesNotExist,
                               msg="We deleted the user from the database but he was not automatically excluded "
                                   "from the group"):
            GroupUser.objects.get(group_id=obj.entity.id, user_id=user_id)

    def test_group_user_double_remove(self):
        obj, new_user = self._create_test_group_users_precondition()
        obj.entity.users.add(new_user)
        obj.entity.users.remove(new_user)
        obj.entity.users.remove(new_user)
        obj.reload_entity()
        self._check_test_group_users_preconditions(obj)
        self.assertFalse(obj.entity.users.exists(new_user),
                         "Unable to remove user from the group")

    @parameterized.expand([("add",), ("remove",)])
    def test_user_operations_on_removing_group(self, operation):
        obj = GroupObject()
        obj.entity.create()
        user = User(login="vasya.petrov")
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Non-existent user was successfully added to the group"):
            obj.entity.users.add(user)
        user.create()
        obj.entity.delete()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="Non-existent user was successfully added to removed group"):
            getattr(obj.entity.users, operation)(user)

    def test_add_user_to_creating_group(self):
        obj = GroupObject()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The user was successfully created to inexistent group"):
            obj.entity.users.add(obj.entity.governor)

    def test_add_governor(self):
        obj = GroupObject()
        obj.create_entity()
        obj.entity.users.add(obj.entity.governor)
        self._check_default_fields(obj.entity)

    def test_remove_governor(self):
        obj = GroupObject()
        obj.create_entity()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The governor was successfully removed from the group"):
            obj.entity.users.remove(obj.entity.governor)

    def test_remove_governor_non_trivial(self):
        user = User(login="vasily.petrov")
        user.create()
        group = GroupObject(governor=user)
        group.create_entity()
        with self.assertRaises(GroupGovernorConstraintFails,
                               msg="The group governor was successfully deleted that results to unexpected changes"
                                   "in corresponding group"):
            user.delete()

    def test_users_len(self):
        obj = GroupObject()
        obj.create_entity()
        self.assertEquals(len(obj.entity.users), 1, "All users have been created")

    def test_users_iteration(self):
        obj = GroupObject()
        obj.create_entity()
        for user in obj.entity.users:
            self.assertEquals(user, self.__test_user, "The group must contain one use only for this test case")

    def test_user_index_positive(self):
        obj = GroupObject()
        obj.create_entity()
        self.assertEquals(obj.entity.users[0], self.__test_user,
                          "The user containing in the test group is not a test user")

    def test_user_index_negative(self):
        obj = GroupObject()
        obj.create_entity()
        with self.assertRaises(EntityNotFoundException,
                               msg="The user with non-existent index is suddenly found within the group's user list"):
            print(obj.entity.users[1])

    def _create_test_group_users_precondition(self):
        obj = GroupObject()
        obj.create_entity()
        for n in range(10):
            user_login = "user%d" % n
            user = User(login=user_login)
            user.create()
            obj.entity.users.add(user)
        obj.reload_entity()
        User(login="new_user").create()
        return obj, UserSet().get("new_user")

    def _check_test_group_users_preconditions(self, obj):
        self._check_default_fields(obj.entity)
        self.assertTrue(obj.entity.users.exists(self.__test_user), "The group governor does not exist in the group")
        for n in range(10):
            user_login = "user%d" % n
            user = UserSet().get(user_login)
            self.assertTrue(obj.entity.users.exists(user))

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(entity.name, "Группа оптического картирования", "The group name doesn't retrieve correctly")
        self.assertEquals(entity.governor, self.__test_user, "The group governor doesn't retrieve correctly")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param entity: the entity to store
        :return: nothing
        """
        self.assertEquals(entity.name, "Вазомоторные колебания", "The group name doesn't changed correctly")
        self.assertEquals(entity.governor, self.__test_user, "The group governor doesn't retrieve correctly")


del BaseTestClass
