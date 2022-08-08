from django.conf import settings
from django.test import TestCase
from parameterized import parameterized

from core.os.group import PosixGroup, OperatingSystemGroupNotFound

from .base_command_test import BaseOsFeatureTest


class TestPosixGroup(BaseOsFeatureTest):
    """
    All test routines for the core.os.group.PosixGroup class
    """

    def setUp(self):
        if not settings.CORE_UNIX_ADMINISTRATION or not settings.CORE_MANAGE_UNIX_GROUPS:
            self.skipTest("The tested features are not available under given system configuration")
        super().setUp()

    def test_iteration(self):
        """
        Testing iterate() routine
        """
        for group in PosixGroup.iterate():
            self.assertTrue(group.registered, "The currently found group shall be marked as 'registered'")

    def test_find_by_name(self):
        """
        Tests the find_by_name routine
        """
        root_group = PosixGroup.find_by_name("root")
        self.assert_root_group(root_group)

    def test_find_by_gid(self):
        """
        Tests the find_by_gid routine
        """
        root_group = PosixGroup.find_by_gid(0)
        self.assert_root_group(root_group)

    @parameterized.expand([
        ("some_group", True),
        ("", False),
        (None, False)
    ])
    def test_create_group(self, name, is_name_valid):
        if is_name_valid:
            group = PosixGroup(name=name)
            self.assertEquals(group.name, name, "Undesirable group name")
            self.assertIsNone(group.gid, "Sudden GID")
            self.assertFalse(group.registered, "The group has been suddenly registered")
            group.create()
            self._maker.run_all_commands()
            self.assertEquals(group.name, name, "The group name has been suddenly changed after its create")
            self.assertTrue(group.registered, "The group has not been marked as 'registered' after its create")
            group_copy = PosixGroup.find_by_name(name)
            self.assertIsNotNone(group_copy.gid, "The group GID has not been assigned after reloading")
            self.assertTrue(group_copy.registered, "The group has not been marked as 'registered' after reloading")
            self.assertEquals(len(group_copy.user_list), 0, "The group contains some predefined members")
            group.delete()
            self._maker.run_all_commands()
        else:
            with self.assertRaises(ValueError, msg="Negative test for group create has not been failed"):
                PosixGroup(name=name)

    def test_delete_group(self):
        group = PosixGroup(name="some")
        group.create()
        self._maker.run_all_commands()
        group2 = PosixGroup.find_by_name("some")
        group2.delete()
        self._maker.run_all_commands()
        self.assertFalse(group2.registered, "The group shall be marked as 'unregistered' after its delete")
        with self.assertRaises(OperatingSystemGroupNotFound, msg="The group is still present in the system even after its delete"):
            PosixGroup.find_by_name("some")

    def test_update_group(self):
        group = PosixGroup(name="group1")
        group.create()
        self._maker.run_all_commands()
        group2 = PosixGroup.find_by_name("group1")
        group2.name = "group2"
        group2.update()
        self._maker.run_all_commands()
        group3 = PosixGroup.find_by_name("group2")
        self.assertEquals(group3.gid, group2.gid, "The group GID has been suddenly changed when changing the group name")
        group3.delete()
        self._maker.run_all_commands()

    def assert_root_group(self, root_group):
        """
        Asserts that the root group has standard POSIX properties

        :param root_group: the root group to be checked
        :return: nothing
        """
        self.assertEquals(root_group.name, "root", "The root group must have 'root' name")
        self.assertEquals(root_group.gid, 0, "The root group must have GID=0")
        self.assertTrue(root_group.registered, "The root group must be already registered")
        if len(root_group.user_list) > 0:
            self.assertIn("root", root_group.user_list, "The root group must contain the 'root' user")


del BaseOsFeatureTest
