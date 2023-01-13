from random import randrange

from django.contrib.auth.hashers import make_password, check_password

from core.entity.entity_fields.field_managers.entity_value_manager import EntityValueManager


class EntityPasswordManager(EntityValueManager):
    """
    Manager all field passwords
    """

    SMALL_LATIN_LETTERS = "abcdefghijklmnopqrstuvwxyz"
    BIG_LATIN_LETTERS = SMALL_LATIN_LETTERS.upper()
    LATIN_LETTERS = SMALL_LATIN_LETTERS + BIG_LATIN_LETTERS
    DIGITS = "0123456789"
    SPECIAL_SYMBOLS = "!@#$%^&*()_+=-~`\\\";:'/?.>,<"
    ALL_SYMBOLS = LATIN_LETTERS + DIGITS + SPECIAL_SYMBOLS

    @classmethod
    def generate_password(cls, allowed_symbols: str, size: int) -> str:
        """
        The function generates new password and just saves it
        :param size: the password size
        :param allowed_symbols: symbols that can be contained in the password.
        :return: newly generated password
        """
        password = ""
        for i in range(size):
            index = randrange(len(allowed_symbols))
            symbol = allowed_symbols[index]
            password += symbol
        return password

    def generate(self, allowed_symbols: str, size: int) -> str:
        """
        The function generates new password, saves the password to the private entity field (not to the database!)
        and returns the newly generated password as a result

        :param size: the password size
        :param allowed_symbols: symbols that can be contained in the password.
        :return: the newly generated password
        """
        password = self.generate_password(allowed_symbols, size)
        password_hash = make_password(password)
        setattr(self.entity, "_" + self.field_name, password_hash)
        self.entity.notify_field_changed(self.field_name)
        return password

    def clear(self):
        """
        Clears the previously generated password. This function will not save information to the database

        :return:
        """
        setattr(self.entity, "_" + self.field_name, None)
        self.entity.notify_field_changed(self.field_name)

    def check(self, password: str) -> bool:
        """
        Checks whether the password is valid

        :param password: the password that is needed to be checked
        :return: True if the password is guessed, False otherwise
        """
        encoded_password = getattr(self.entity, "_" + self.field_name)
        if encoded_password is None or encoded_password == "":
            return False
        return check_password(password, encoded_password)

    def __repr__(self):
        """
        If the user attempts to print the password using the repr() function, the code below will show him
        that the password exists but nobody can see it

        :return: password placeholder
        """
        if self._field_value is not None:
            return "**********"
        else:
            return ""
