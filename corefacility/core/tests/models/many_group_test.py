from django.test import TestCase
from core.models import User, Group, GroupUser


class ManyGroupTest(TestCase):
    USER_NUMBER = 20
    GROUP_NUMBER = 5

    LOGIN_PREFIX = "user_"
    GROUP_NAME_PREFIX = "Группа "

    user_list = None
    group_list = None
    project = None

    @classmethod
    def setUpTestData(cls):
        cls.group_list = []
        cls.user_list = []
        for n in range(cls.USER_NUMBER):
            user = User(login=cls.LOGIN_PREFIX + str(n))
            user.save()
            cls.user_list.append(user)
        for n in range(cls.GROUP_NUMBER):
            group = Group(name=cls.GROUP_NAME_PREFIX + str(n))
            group.save()
            cls.group_list.append(group)
        for n in range(cls.USER_NUMBER):
            cls._add_user_to_group(cls.group_list[0], cls.user_list[n])
            if n % 2 == 0:
                cls._add_user_to_group(cls.group_list[1], cls.user_list[n])
            if n % 4 == 0:
                cls._add_user_to_group(cls.group_list[2], cls.user_list[n])
            if n % 5 == 0:
                cls._add_user_to_group(cls.group_list[3], cls.user_list[n])
            if n % 10 == 0:
                cls._add_user_to_group(cls.group_list[4], cls.user_list[n])

    @classmethod
    def _add_user_to_group(cls, group, user):
        GroupUser(group=group, user=user, is_governor=False).save()
