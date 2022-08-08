from django.conf import settings
from parameterized import parameterized

from core.os.user.exceptions import OperatingSystemUserNotFoundException
from core.os.user import PosixUser

from .base_command_test import BaseOsFeatureTest


def common_data_provider():
    return [
        ("sergei.kozhukhov", "Сергей", "Кожухов", "sergei.kozhukhov@ihna.ru", "982374789", "/home/sergei.kozhukhov"),
    ]


# noinspection PyTypeChecker
def create_user_provider():
    return [
               (*user_data, True) for user_data in common_data_provider()
           ] + [

               ("", "Сергей", "Кожухов", "sergei.kozhukhov@ihna.ru", "2893678423", "/home/sergei.kozhukhov", False),
               (None, "Сергей", "Кожухов", "sergei.kozhukhov@ihna.ru", "21893647823", "/home/sergei.kozhukhov", False),

               ("sergei.kozhukhov", "", "Кожухов", "sergei.kozhukhov@ihna.ru", "2894567894", "/home/sergei.kozhukhov",
                True),
               (
                   "sergei.kozhukhov", None, "Кожухов", "sergei.kozhukhov@ihna.ru", "28935677894",
                   "/home/sergei.kozhukhov",
                   True),

               ("sergei.kozhukhov", "Сергей", "", "sergei.kozhukhov@ihna.ru", "9023789423", "/home/sergei.kozhukhov",
                True),
               ("sergei.kozhukhov", "Кожухов", None, "sergei.kozhukhov@ihna.ru", "28073589", "/home/sergei.kozhukhov",
                True),

               (
                   "sergei.kozhukhov", "Сергей", "Кожухов", "sergei.kozhukhov@ihna.ru", "", "/home/sergei.kozhukhov",
                   True),
               ("sergei.kozhukhov", "Сергей", "Кожухов", "sergei.kozhukhov@ihna.ru", None, "/home/sergei.kozhukhov",
                True),

               ("sergei.kozhukhov", "Сергей", "Кожухов", "sergei.kozhukhov@ihna.ru", "982374789", None, False),
           ]


class TestPosixUser(BaseOsFeatureTest):
    _initial_users = None

    def setUp(self):
        if not settings.CORE_MANAGE_UNIX_USERS or not settings.CORE_UNIX_ADMINISTRATION:
            self.skipTest("The test is not required for a given configuration")
        super().setUp()

    @parameterized.expand(create_user_provider())
    def test_create(self, login, name, surname, email, phone, home_dir, is_success=True):
        """
        Tests whether the user can be created successfully
        """
        if is_success:
            user = self.create_new_user(login, name, surname, email, phone, home_dir)
            another_user = self.reload_user(user)
            self.check_user(another_user, login, name, surname, email, phone, home_dir)
        else:
            with self.assertRaises(Exception, msg="The negative test case has been executed successfully"):
                self.create_new_user(login, name, surname, email, phone, home_dir)

    @parameterized.expand(common_data_provider())
    def test_update(self, *user_info):
        user = self.create_new_user(*user_info)
        user2 = self.reload_user(user)
        user2.name = "The Name"
        user2.update()
        self._maker.run_all_commands()
        user3 = self.reload_user(user2)
        self.assertEquals(user3.login, user2.login, "Logins are not the same")

    @parameterized.expand(common_data_provider())
    def test_delete(self, *user_info):
        """
        Tests the user delete
        """
        user = self.create_new_user(*user_info)
        user2 = self.reload_user(user)
        user2.delete()
        self._maker.run_all_commands()
        self.assertEquals(user2.registered, False, "The user shall be marked as 'unregistered' after the user delete")
        with self.assertRaises(OperatingSystemUserNotFoundException,
                               msg="The user can still be found even after account delete"):
            PosixUser.find_by_login("sergei.kozhukhov")

    def create_new_user(self, login, name, surname, email, phone, home_dir):
        user = PosixUser(login=login, name=name, surname=surname, email=email, phone=phone, home_directory=home_dir)
        self.assertFalse(user.registered, "Please, create() the user if you want it to be registered()")
        user.create()
        self.assertTrue(user.registered, "The user() must be registered after the create() command")
        self._maker.run_all_commands()
        return user

    def reload_user(self, user):
        user = PosixUser.find_by_login(user.login)
        self.assertTrue(user.registered, "The currently loaded user must be marked as 'registered'")
        return user

    def check_user(self, another_user, login, name, surname, email, phone, home_dir):
        if login is not None:
            self.assertEquals(another_user.login, login, "Incorrect user login")
        if name is not None:
            self.assertEquals(another_user.name, name, "Incorrect user name")
        if surname is not None:
            self.assertEquals(another_user.surname, surname, "Incorrect user surname")
        if phone is not None:
            self.assertEquals(another_user.phone, phone, "Incorrect user phone")
        if home_dir is not None:
            self.assertEquals(another_user.home_dir, home_dir, "Incorrect home directory")


del BaseOsFeatureTest
