import os
import stat
import hashlib
from subprocess import run

from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from parameterized import parameterized

from core.entity.user import UserSet
from core.entity.entity_providers.posix_providers.user_provider import UserProvider as PosixProvider
from core.os.user import PosixUser, LockStatus, OperatingSystemUserNotFoundException
from core.test.views.field_test.data_providers import \
    slug_provider, arbitrary_string_provider, phone_provider


def base_data_provider():
    return {
        "login": "sergei_kozhukhov",
        "name": "Сергей",
        "surname": "Кожухов",
        "email": "sergei.kozhukhov@ihna.ru",
    }


def input_data_provider():
    # noinspection PyTypeChecker
    return [
               (base_data_provider(),),
           ] + [
               ({
                    "login": login,
                    "name": "Сергей",
                    "surname": "Кожухов",
                    "email": "sergei.kozhukhov@ihna.ru",
                },)
               for login, is_valid in slug_provider(100) if is_valid
           ] + [
               ({
                    "login": "sergei_kozhukhov",
                    "name": name,
                    "surname": "Кожухов",
                    "email": "sergei.kozhukhov@ihna.ru",
                },)
               for name, is_valid in arbitrary_string_provider(True, 100) if is_valid
           ] + [
               ({
                    "login": "sergei_kozhukhov",
                    "name": "Сергей",
                    "surname": surname,
                    "email": "sergei.kozhukhov@ihna.ru",
                },)
               for surname, is_valid in arbitrary_string_provider(True, 100) if is_valid
           ] + [
               ({
                    "login": "sergei_kozhukhov",
                    "name": "Сергей",
                    "surname": "Кожухов",
                    "email": "sergei.kozhukhov@ihna.ru",
                    "phone": phone
                },)
               for phone, is_valid in phone_provider() if is_valid
           ]


def partial_update_provider():
    return [("login", login) for login, is_valid in slug_provider(100) if is_valid] + \
           [("name", name) for name, is_valid in arbitrary_string_provider(True, 100) if is_valid] + \
           [("surname", surname) for surname, is_valid in arbitrary_string_provider(True, 100) if is_valid] + \
           [("phone", phone) for phone, is_valid in phone_provider() if is_valid]


class TestUserProvider(APITestCase):
    API_VERSION = "v1"
    LOGIN_REQUEST = "/api/{version}/login/".format(version=API_VERSION)
    USER_LIST_PATH = "/api/{version}/users/".format(version=API_VERSION)
    USER_DETAIL_PATH = "/api/{version}/users/%d/".format(version=API_VERSION)
    PASSWORD_RESET_PATH = "/api/{version}/users/%d/password-reset/".format(version=API_VERSION)

    TEST_FILENAME = "test.txt"
    TEST_FILE_CONTENT = "Hello, World!"

    auth_headers = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        result = APIClient().post(cls.LOGIN_REQUEST)
        token = result.data['token']
        cls.auth_headers = {"HTTP_AUTHORIZATION": "Token " + token}

    def setUp(self):
        super().setUp()
        if not PosixProvider().is_provider_on() or not settings.CORE_UNIX_ADMINISTRATION:
            self.skipTest("The test can't be launched under given configuration")

    @parameterized.expand(input_data_provider())
    def test_create_user(self, input_data):
        """
		Tests whether POSIX account is created automatically when the user is created 
		"""
        result = self._create_user(input_data)
        posix_user = PosixUser.find_by_login(result.data['unix_group'])
        self._assert_gecos_information(input_data, result.data, posix_user)
        self.assertNotEqual(posix_user.is_locked(), LockStatus.PASSWORD_SET,
                            "The password must not be turned to SET")
        self._assert_home_directory(result.data, posix_user)
        self._delete_user(result.data['id'])
        self._assert_user_delete(result)
        self._assert_no_home_directory(result.data)

    @parameterized.expand(input_data_provider())
    def test_double_create(self, input_data):
        """
		Tests whether the 'POSIX account already exists' errors are suppressed
		"""
        self._create_posix_user(input_data['login'])
        result = self._create_user(input_data)
        posix_user = PosixUser.find_by_login(result.data['unix_group'])
        self._assert_gecos_information(input_data, result.data, posix_user)
        self._assert_home_directory(result.data, posix_user)
        self._delete_user(result.data['id'])
        self._assert_user_delete(result)

    @parameterized.expand(partial_update_provider())
    def test_partial_update(self, field_name, field_value):
        """
		Tests whether POSIX user accounts are successfully updated when POSIX users are updated
		"""
        initial_data = base_data_provider()
        preliminary_result = self._create_user(initial_data)
        user_id = preliminary_result.data['id']
        result = self.client.patch(self.USER_DETAIL_PATH % user_id,
                                   {field_name: field_value}, format="json", **self.auth_headers)
        if result.status_code != status.HTTP_200_OK:
            print(result, result.data)
        self.assertEquals(result.status_code, status.HTTP_200_OK, "Unexpected status code")
        initial_data[field_name] = field_value
        posix_user = PosixUser.find_by_login(result.data['unix_group'])
        self._assert_gecos_information(initial_data, result.data, posix_user)
        self._assert_home_directory(result.data, posix_user)
        self._delete_user(result.data['id'])
        self._assert_user_delete(result)

    @parameterized.expand(partial_update_provider())
    def test_extra_update(self, field_name, field_value):
        """
		Tests whether POSIX user accounts can be successfully updated even after their deleting
		"""
        initial_data = base_data_provider()
        preliminary_result = self._create_user(initial_data)
        user_id = preliminary_result.data['id']
        self._delete_posix_user(preliminary_result.data['unix_group'])
        result = self.client.patch(self.USER_DETAIL_PATH % user_id,
                                   {field_name: field_value}, format="json", **self.auth_headers)
        self.assertEquals(result.status_code, status.HTTP_200_OK, "Unexpected status code")
        initial_data[field_name] = field_value
        posix_user = PosixUser.find_by_login(result.data['unix_group'])
        self._assert_gecos_information(initial_data, result.data, posix_user)
        self._assert_home_directory(result.data, posix_user)
        self._delete_user(result.data['id'])
        self._assert_user_delete(result)
        self._assert_no_home_directory(result.data)

    def test_password_and_locked(self):
        """
		Tests the password and locking feature
		"""
        initial_data = base_data_provider()
        initial_result = self._create_user(initial_data)
        user_id = initial_result.data['id']
        posix_user = PosixUser.find_by_login(initial_result.data['unix_group'])
        password_result = self.client.post(self.PASSWORD_RESET_PATH % user_id, **self.auth_headers)
        self.assertEquals(password_result.status_code, status.HTTP_200_OK,
                          "Unexpected response code for password reset")
        password = password_result.data['password']
        user = UserSet().get(initial_result.data['login'])
        self.assertEquals(posix_user.is_locked(), LockStatus.PASSWORD_SET,
                          "Incorrect lock status for the POSIX account after password reset")
        self.assertTrue(user.password_hash.check(password),
                        "The password has not been cleared")
        locking_result = self.client.patch(self.USER_DETAIL_PATH % user_id,
                                           {"is_locked": True}, **self.auth_headers)
        self.assertEquals(locking_result.status_code, status.HTTP_200_OK,
                          "The user locking has been failed")
        self.assertEquals(posix_user.is_locked(), LockStatus.LOCKED,
                          "Unable to lock the POSIX user")
        unlocking_result = self.client.patch(self.USER_DETAIL_PATH % user_id,
                                             {"is_locked": False}, **self.auth_headers)
        self.assertEquals(posix_user.is_locked(), LockStatus.PASSWORD_SET,
                          "Unable to unlock the POSIX user")
        self._delete_user(user_id)
        self._assert_user_delete(unlocking_result)

    def _create_user(self, input_data):
        """
		Creates the user using API
		:param input_data: the user input data
		:return: the HTTP response. The response is asserted to be 201
		"""
        result = self.client.post(self.USER_LIST_PATH, input_data, format="json",
                                  **self.auth_headers)
        if result.status_code != status.HTTP_201_CREATED:
            print(result, result.data)
        self.assertEquals(result.status_code, status.HTTP_201_CREATED,
                          "Unexpected status code")
        return result

    def _assert_home_directory(self, user_info, posix_user):
        home_dir = user_info['home_dir']
        self.assertTrue(os.path.isdir(home_dir))
        stat_info = os.stat(home_dir)
        self.assertEquals(stat_info.st_uid, posix_user.uid, "The home directory owner doesn't correspond to its user")
        self.assertEquals(stat_info.st_gid, posix_user.gid, "The home directory's owning group doesn't correspond to the owner's primary group")
        self.assertEquals(stat.S_IMODE(stat_info.st_mode), 0o4750, "The permission rights for the user's home directory are not appropriate")
        with open(self.TEST_FILENAME, "w") as test_file:
            test_file.write(self.TEST_FILE_CONTENT)

    def _assert_no_home_directory(self, user_info):
        home_dir = user_info['home_dir']
        self.assertFalse(os.path.isdir(home_dir), "The user's home directory has not been deleted together with the user's delete")

    def _assert_gecos_information(self, input_data, output_data, posix_user):
        """
		Asserts that the user's name, surname and phone are properly saved in the POSIX account
		:param input_data: the input data used for creating the account
		:param output_data: the output data
		:param posix_user: a PosixUser instance
		:return: nothing
		"""
        self.assertEquals(output_data['login'], input_data['login'], "Logins are not the same")
        if posix_user.name != '':
            self.assertEquals(posix_user.name, input_data['name'], "User names are not the same")
        if posix_user.surname != '':
            self.assertEquals(posix_user.surname, input_data['surname'], "User surnames are not the same")
        if 'phone' in input_data and posix_user.phone != '':
            self.assertEquals(posix_user.phone, input_data['phone'], "User phones are not the same")

    def _delete_user(self, user_id):
        """
		Deletes the user using the HTTP request
		:param user_id: User's ID
		:return: nothing
		"""
        final_result = self.client.delete(self.USER_DETAIL_PATH % user_id, **self.auth_headers)
        self.assertEquals(final_result.status_code, status.HTTP_204_NO_CONTENT,
                          "The user can't be deleted successfully after all assertions")

    def _assert_user_delete(self, result):
        with self.assertRaises(OperatingSystemUserNotFoundException,
                               msg="The user record is still presented in the operating system even after its delete"):
            PosixUser.find_by_login(result.data['unix_group'])

    def _create_posix_user(self, user_login):
        """
		Creates the POSIX user directly
		:param user_login: user's login
		:return: nothing
		"""
        if len(user_login) > PosixUser.get_max_login_chars():
            posix_login = hashlib.md5(user_login.encode("utf-8")).hexdigest()
        else:
            posix_login = user_login
        run(("useradd", posix_login))

    def _delete_posix_user(self, user_login):
        """
		Deletes the POSIX user directly
		:param user_login: user's login
		:return: nothing
		"""
        run(("userdel", user_login))
