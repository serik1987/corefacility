from parameterized import parameterized
from rest_framework import status

from core.entity.user import UserSet
from core.test.entity_set.entity_set_objects.user_set_object import UserSetObject

from .base_test_class import BaseTestClass, profile_provider


def security_test_provider():
    return [
        (*profile, token_id, expected_status_code)
        for profile in profile_provider()
        for (token_id, expected_status_code) in [
            (None, status.HTTP_401_UNAUTHORIZED),
            ("ordinary_user", status.HTTP_403_FORBIDDEN),
        ]
    ]


def name_provider():
    return [
        (name, *profile)
        for name in ["Иванов", "Миронова", "ов", "Сергей", "Полина", "user1", "user10", "support", "xxx", ""]
        for profile in profile_provider()
    ]


class TestUser(BaseTestClass):
    """
    This function tests user lists and looking throw user lists
    """

    superuser_required = True
    ordinary_user_required = True
    _request_path = "/api/{version}/users/".format(version=BaseTestClass.API_VERSION)

    _user_set_object = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._user_set_object = UserSetObject()

    def setUp(self):
        super().setUp()
        self._container = self._user_set_object.clone()
        self._container.sort()
        user_set = UserSet()
        user = user_set.get("user")
        self._container.entities.insert(0, user)
        superuser = user_set.get("superuser")
        self._container.entities.insert(0, superuser)
        support = user_set.get("support")
        self._container.entities.insert(0, support)

    @parameterized.expand(profile_provider())
    def test_general_search(self, profile):
        query_params = {"profile": profile}
        self._test_search(query_params, "superuser")

    @parameterized.expand(security_test_provider())
    def test_security(self, profile, token_id, expected_status_code):
        query_params = {"profile": profile}
        self._test_search(query_params, token_id, expected_status_code)

    @parameterized.expand(name_provider())
    def test_name_filter(self, name, profile):
        self.container.filter_by_name(name)
        query_params = {"q": name, "profile": profile}
        self._test_search(query_params, "superuser")

    def assert_items_equal(self, actual_item, desired_item):
        """
        Compares two list item

        :param actual_item: the item received within the response
        :param desired_item: the item taken from the container
        :return: nothing
        """
        description = "Actual user: %s. Desired user: %s" % (repr(actual_item), repr(desired_item))
        self.assertEquals(actual_item['id'], desired_item.id,
                          "Item IDs are not the same. " + description)
        self.assertEquals(actual_item['login'], desired_item.login, "Item logins are not the same. " + description)
        self.assertEquals(actual_item['avatar'], desired_item.avatar.url, "Item avatars are not the same. " + description)
        self.assertEquals(actual_item['name'], desired_item.name, "Item names are not the same. " + description)
        self.assertEquals(actual_item['surname'], desired_item.surname, "Item surnames are not the same. " + description)


del BaseTestClass
