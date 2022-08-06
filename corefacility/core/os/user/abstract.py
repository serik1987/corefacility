from .exceptions import OperatingSystemUserNotFoundException, OperatingSystemUserLoginTooLarge


class AbstractUser:
    """
    Describes the interface of how the user package will be interacted with the rest of the application.

    Contains abstract methods only. Such methods must be implemented for any kind of supported operating system
    """

    USER_LIST_FILE = "/etc/passwd"

    _login = None
    _name = None
    _surname = None
    _email = None
    _phone = None
    _home_directory = None

    _registered = False

    @classmethod
    def get_max_login_chars(cls):
        """
        :return: Maximum characters in the login
        """
        raise NotImplementedError("get_max_login_chars")

    @classmethod
    def iterate(cls):
        """
        Iterates over all user records within the operating system (system records must be omitted)

        :return: generator to be user in for loop
        """
        raise NotImplementedError("iterate")

    @classmethod
    def find_by_login(cls, login):
        """
        Finds a user with a given login. Throws OperatingSystemUserNotFoundException when the user was not found

        :param login: a login to be used
        :return:a user with given login
        """
        for user in cls.iterate():
            if user.login == login:
                return user
        raise OperatingSystemUserNotFoundException(login)

    def __init__(self, login=None, name=None, surname=None, email=None, phone=None, home_directory=None):
        """
        Creates a copy of the user but doesn't add the user record to the operating system (use create() method
        for such purpose)

        :param login: desired user login
        :param name: the first name
        :param surname: the last name
        :param email: email
        :param phone: phone
        :param home_directory: home directory
        """
        self.login = login
        self._name = name
        self._surname = surname
        self._email = email
        self._phone = phone
        self._home_directory = home_directory

    @property
    def login(self):
        """
        The SSH login
        """
        return self._login

    @login.setter
    def login(self, new_login):
        """
        Sets the new login value
        :param new_login: new login value to be set
        :return: nothing
        """
        if isinstance(new_login, str) and 0 < len(new_login) < self.get_max_login_chars():
            self._login = new_login
        else:
            raise OperatingSystemUserLoginTooLarge(new_login)

    @property
    def name(self):
        """
        User's first name
        """
        return self._name

    @property
    def surname(self):
        """
        User's surname
        """
        return self._surname

    @property
    def email(self):
        """
        User's e-mail
        """
        return self._email

    @property
    def phone(self):
        """
        User's phone
        """
        return self._phone

    @property
    def home_dir(self):
        """
        User's home directory
        """
        return self._home_directory

    @property
    def registered(self):
        """
        True if the user record has been presented inside the operating system, False otherwise
        """
        return self._registered

    def create(self):
        """
        Creates a user record in the operating system using the information passed as constructor arguments

        :return: nothing
        """
        raise NotImplementedError("create")

    def delete(self):
        """
        Deletes a user record from the operating system

        :return: nothing
        """
        raise NotImplementedError("delete")

    def set_password(self, password):
        """
        Sets the user password

        :param password: a non-encrypted password to be set
        :return: nothing
        """
        raise NotImplementedError("set_password")

    def clear_password(self):
        """
        Clears the user password

        :return: nothing
        """
        raise NotImplementedError("clear_password")

    def lock(self):
        """
        Locks the user

        :return: nothing
        """
        raise NotImplementedError("lock")

    def unlock(self):
        """
        Unlocks the user

        :return: nothing
        """
