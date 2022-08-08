from django.conf import settings
from parameterized import parameterized

from core.os.user.exceptions import OperatingSystemUserNotFoundException
from core.os.user import PosixUser
from core.os.group import PosixGroup

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
    _user_set_object = None

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
        user2.name = "TheName"
        user2.update()
        self._maker.run_all_commands()
        user3 = self.reload_user(user2)
        self.assertEquals(user3.name, user2.name, "Logins are not the same")

    @parameterized.expand(common_data_provider())
    def test_login_update(self, *user_info):
        user = self.create_new_user(*user_info)
        user2 = self.reload_user(user)
        user2.login = "another_login"
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

    def test_group_belonging(self):
        """
        Tests how the user can be added to the group
        """
        self._create_posix_user_set()
        self._create_posix_group_set()
        self._connect_posix_users_from_set()
        self._maker.run_all_commands()
        self._assert_user_list()
        self._delete_posix_group_set()
        self._maker.run_all_commands()

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

    def _create_posix_user_set(self):
        self._mironova = PosixUser(login="ekaterina.mironova", name="Екатерина", surname="Миронова", home_directory="/home/mironova")
        self._mironova.create()
        self._zolotova = PosixUser(login="polina.zolotova", name="Полина", surname="Золотова", home_directory="/home/zolotova")
        self._zolotova.create()
        self._orekhova = PosixUser(login="maria.orekhova", name="Мария", surname="Орехова", home_directory="/home/orekhova")
        self._orekhova.create()
        self._pavlov = PosixUser(login="ilja.pavlov", name="Илья", surname="Павлов", home_directory="/home/pavlov")
        self._pavlov.create()
        self._tsvetkov = PosixUser(login="leon.tsvetkov", name="Леон", surname="Цветков", home_directory="/home/tsvetkov")
        self._tsvetkov.create()
        self._solovieva = PosixUser(login="daria.solovieva", name="Дарья", surname="Соловьёва", home_directory="/home/solovieva")
        self._solovieva.create()
        self._komarov = PosixUser(login="artem.komarov", name="Артём", surname="Комаров", home_directory="/home/komarov")
        self._komarov.create()
        self._dmitriev = PosixUser(login="ilja.dmitriev", name="Илья", surname="Дмитриев", home_directory="/home/dmitriev")
        self._dmitriev.create()
        self._spiridonova = PosixUser(login="anastasia.spiridonova", name="Анастасия", surname="Спиридонова", home_directory="/home/spiridonova")
        self._spiridonova.create()
        self._sytchov = PosixUser(login="alexander.sytchov", name="Александр", surname="Сычёв", home_directory="/home/sytchov")
        self._sytchov.create()

    def _create_posix_group_set(self):
        PosixGroup(name="g0").create()
        PosixGroup(name="g1").create()
        PosixGroup(name="g2").create()
        PosixGroup(name="g3").create()
        PosixGroup(name="g4").create()

    def _connect_posix_users_from_set(self):
        self._mironova.set_groups(("g0", "g1"))
        self._zolotova.set_groups(("g0",))
        self._orekhova.set_groups(("g0", "g1"))
        self._pavlov.set_groups(("g1", "g2"))
        self._tsvetkov.set_groups(("g1", "g2"))
        self._solovieva.set_groups(("g0", "g2", "g3"))
        self._komarov.set_groups(("g2", "g3", "g4"))
        self._dmitriev.set_groups(("g3", "g4"))
        self._spiridonova.set_groups(("g3", "g4"))
        self._sytchov.set_groups(("g4",))

    def _assert_user_list(self):
        for group in PosixGroup.iterate():
            if group.name == "g0":
                self.assertEquals(group.user_list, ['ekaterina.mironova', 'polina.zolotova', 'maria.orekhova', 'daria.solovieva'],
                    "The first group has unexpected user list")
            if group.name == "g1":
                self.assertEquals(group.user_list, ['ekaterina.mironova', 'maria.orekhova', 'ilja.pavlov', 'leon.tsvetkov'])
            if group.name == "g2":
                self.assertEquals(group.user_list, ['ilja.pavlov', 'leon.tsvetkov', 'daria.solovieva', 'artem.komarov'])
            if group.name == "g3":
                self.assertEquals(group.user_list, ['daria.solovieva', 'artem.komarov', 'ilja.dmitriev', 'anastasia.spiridonova'])
            if group.name == "g4":
                self.assertEquals(group.user_list, ['artem.komarov', 'ilja.dmitriev', 'anastasia.spiridonova', 'alexander.sytchov'])

    def _delete_posix_group_set(self):
        groups = []
        for group in PosixGroup.iterate():
            if group.name in ["g0", "g1", "g2", "g3", "g4"]:
                groups.append(group)
        for group in groups:
            group.delete()


del BaseOsFeatureTest
