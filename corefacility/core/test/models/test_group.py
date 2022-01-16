from django.test import TestCase
from parameterized import parameterized
from core.models import User, Group
from .many_group_test import ManyGroupTest


class TestGroup(ManyGroupTest):

    def test_number_count(self):
        self.assertEquals(User.objects.count(), self.USER_NUMBER + 1)
        self.assertEquals(Group.objects.count(), self.GROUP_NUMBER)

    def test_group_names(self):
        for n in range(self.GROUP_NUMBER):
            id = self.group_list[n].id
            group = Group.objects.get(id=id)
            self.assertEquals(group.name, self.GROUP_NAME_PREFIX + str(n))

    @parameterized.expand([(0, 20), (1, 10), (2, 5), (3, 4), (4, 2)])
    def test_user_number_for_group(self, group_index, user_number):
        id = self.group_list[group_index].id
        group = Group.objects.get(id=id)
        self.assertEquals(group.users.count(), user_number, "Failed to establish links between users and groups")

    @parameterized.expand([(0, 5), (1, 1), (2, 2), (3, 1), (4, 3), (5, 2), (6, 2), (7, 1), (8, 3), (9, 1), (10, 4),
                           (11, 1), (12, 3), (13, 1), (14, 2), (15, 2), (16, 3), (17, 1), (18, 2), (19, 1)])
    def test_group_number_for_user(self, user_index, group_number):
        old_user = self.user_list[user_index]
        new_user = User.objects.get(id=old_user.id)
        self.assertEquals(new_user.groups.count(), group_number)

    def test_group_delete(self):
        self.group_list[1].delete()
        self.assertEquals(self.user_list[0].groups.count(), 4)
        self.assertEquals(self.user_list[1].groups.count(), 1)
        self.group_list[0].delete()
        self.assertEquals(self.user_list[0].groups.count(), 3)
        self.assertEquals(self.user_list[1].groups.count(), 0)

    def test_user_delete(self):
        self.user_list[0].delete()
        self.assertEquals(self.group_list[0].users.count(), 19)
        self.assertEquals(self.group_list[1].users.count(), 9)
        self.user_list[1].delete()
        self.assertEquals(self.group_list[0].users.count(), 18)
        self.assertEquals(self.group_list[1].users.count(), 9)
