from parameterized import parameterized

from core.entity.user import User
from core.entity.entity_exceptions import EntityFieldInvalid
from core.test.data_providers.field_value_providers import put_stages_in_provider

from .base_test_class import BaseTestClass


def user_provider():
    provided_data = [
        ("main", "alternate", None),
        ("non_existent", "alternate", (EntityFieldInvalid, ValueError)),
        ("deleted", "alternate", (EntityFieldInvalid, ValueError)),
        ("no", "alternate", (EntityFieldInvalid, ValueError)),
        ("invalid", "alternate", (EntityFieldInvalid, ValueError)),
    ]

    return put_stages_in_provider(provided_data)


class TestExternalAuthorizationAccount(BaseTestClass):
    """
    Tests the external authorization account
    """

    _sample_user = None

    _test_users = None

    _user_test_additional_kwargs = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._sample_user = User(login="sergei.kozhukhov", name="Sergei", surname="Kozhukhov")
        cls._sample_user.create()
        cls._entity_object_class.define_default_kwarg("user", cls._sample_user)

        cls._test_users = {
            "main": User(login="vasily.ivanov", name="Vasily", surname="Ivanov"),
            "alternate": User(login="gates1770", name="Bill", surname="Gates"),
            "non_existent": User(login="alexander.petrov", name="Alexander", surname="Petrov"),
            "deleted": User(login="mikhail.sidorov", name="Mikhail", surname="Sidorov"),
            "no": None,
            "invalid": "=== THIS IS A PURELY INVALID VALUE ==="
        }

        cls._test_users["main"].create()
        cls._test_users["alternate"].create()
        cls._test_users["deleted"].create()
        cls._test_users["deleted"].delete()

    @parameterized.expand(user_provider())
    def test_user(self, user, changed_user, throwing_exception, test_number):
        user = self._test_users[user]
        changed_user = self._test_users[changed_user]
        self._test_field("user", user, changed_user, throwing_exception, test_number, use_defaults=False,
                         **self._user_test_additional_kwargs)

    def _check_user_fields(self, account):
        """
        Checks whether all user fields were transmitted correctly given that the user did not re-assigned during
        the standard testing routine.

        :param account: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(account.user.login, "sergei.kozhukhov", "The authorization account was not attached "
                                                                  "to the correct user")
        self.assertEquals(account.user.name, "Sergei", "The account was attached to the user with incorrect name")
        self.assertEquals(account.user.surname, "Kozhukhov",
                          "The account was attached to the user with incorrect surname")
