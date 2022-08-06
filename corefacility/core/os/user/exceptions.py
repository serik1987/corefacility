class OperatingSystemUserNotFoundException(Exception):
    """
    The exception will be risen when there is unable to find a given user
    """

    def __init__(self, login):
        """
        Initializes the exception object
        :param login: login that has been unable to be found
        """
        super().__init__("The user with login '%s' was not found" % login)


class OperatingSystemUserLoginTooLarge(Exception):
    """
    The exception will be risen when the user is trying to input login with too large number of characters
    """

    def __init__(self, login):
        """
        Initializes the exception object
        :param login: login to be entered
        """
        super().__init__("The login '%s' is too large" % login)
