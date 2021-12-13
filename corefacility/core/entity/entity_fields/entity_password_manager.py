from .entity_value_manager import EntityValueManager


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

    def generate(self, allowed_symbols: str, size: int) -> str:
        """
        The function generates new password, saves the password to the private entity field (not to the database!)
        and returns the newly generated password as a result

        :param size: the password size
        :param allowed_symbols: symbols that can be contained in the password.
        :return: the newly generated password
        """
        raise NotImplementedError("TO-DO: EntityPasswordManager.generate")

    def clear(self):
        """
        Clears the previously generated password. This function will not save information to the database

        :return:
        """
        raise NotImplementedError("TO-DO: EntityPasswordManager.clear")

    def check(self, password: str) -> bool:
        """
        Checks whether the password is valid

        :param password: the password that is needed to be checked
        :return: True if the password is guessed, False otherwise
        """
        raise NotImplementedError("TO-DO: EntityPasswordManager.check")
