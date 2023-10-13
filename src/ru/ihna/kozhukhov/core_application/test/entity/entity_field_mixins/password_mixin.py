from ....entity.field_managers.entity_password_manager import EntityPasswordManager


# noinspection PyUnresolvedReferences
class PasswordMixin:
    """
    Contains additional functions to test the password field if it has.

    Use the following sample code to test a single password field:
    @parameterized.expand(password_provider())
    def test_password(self, test_number):
        self._test_password("password_hash", test_number)

    Use token_provider() instead of password_provider() for quick checks
    """

    PASSWORD_TEST_INITIAL = 0
    PASSWORD_TEST_SET = 1
    PASSWORD_TEST_SET_SET = 2
    PASSWORD_TEST_SET_CLEAR = 3
    PASSWORD_TEST_CLEAR = 4
    PASSWORD_STANDARD_SET = ("some-password", "", None)

    def _test_password(self, field_name, test_number):
        """
        Provides a certain password test

        :param field_name: the password field name
        :param test_number: test number
        :return: nothing
        """
        [
            self._test_password_initial,
            self._test_password_was_set,
            self._test_password_was_set_set,
            self._test_password_was_set_clear,
            self._test_password_was_clear_clear,
        ][test_number](field_name)

    def _test_password_initial(self, field_name):
        """
        Checks the initial password state

        :param field_name: name of the password field to test
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        self.assertPasswordsIncorrect(password_field)

    def _test_password_was_set(self, field_name):
        """
        Checks whether the password was set

        :param field_name: name of the password field to test
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        password_field = getattr(obj.entity, field_name)
        password = password_field.generate(EntityPasswordManager.ALL_SYMBOLS, 100)
        obj.entity.update()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        self.assertTrue(password_field.check(password),
                        "The password directly generated by the password field is not correct for the same field")
        self.assertPasswordsIncorrect(password_field)

    def _test_password_was_set_set(self, field_name):
        """
        Checks how the password can be changed

        :param field_name: name of the password field to test
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        password_field = getattr(obj.entity, field_name)
        old_password = password_field.generate(EntityPasswordManager.ALL_SYMBOLS, 100)
        obj.entity.update()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        new_password = password_field.generate(EntityPasswordManager.ALL_SYMBOLS, 100)
        obj.entity.update()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        self.assertTrue(password_field.check(new_password), "The password was changed incorrectly or doesn't changed")
        self.assertPasswordsIncorrect(password_field, [old_password])

    def _test_password_was_set_clear(self, field_name):
        """
        Checks whether the password can be set and cleared again

        :param field_name: name of the password field to test
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        password_field = getattr(obj.entity, field_name)
        old_password = password_field.generate(EntityPasswordManager.ALL_SYMBOLS, 100)
        obj.entity.update()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        password_field.clear()
        obj.entity.update()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        self.assertPasswordsIncorrect(password_field, [old_password])

    def _test_password_was_clear_clear(self, field_name):
        """
        Checks whether cleared password can be cleared again

        :param field_name: name of the password field to test
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        password_field = getattr(obj.entity, field_name)
        password_field.clear()
        obj.entity.update()
        obj.reload_entity()
        password_field = getattr(obj.entity, field_name)
        self.assertPasswordsIncorrect(password_field)

    def assertPasswordsIncorrect(self, password_field: EntityPasswordManager, password_values=None):
        """
        Checks whether password field can reject incorrect passwords

        :param password_field: the password field manager to check
        :param password_values: password values that will be checked in addition to standard password values
        :return: nothing
        """
        if password_values is None:
            password_values = []
        for password in list(self.PASSWORD_STANDARD_SET) + list(password_values):
            self.assertFalse(password_field.check(password),
                             "The following password was successfully guessed: %s" % password)