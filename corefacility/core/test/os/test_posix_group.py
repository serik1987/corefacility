from django.test import TestCase

from core.os.group import PosixGroup


class TestPosixGroup(TestCase):
    """
    All test routines for the core.os.group.PosixGroup class
    """

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
