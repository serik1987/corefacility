class OperatingSystemGroupNotFound(Exception):
    """
    Raises when the module is unable to find the operating system group with a given name or identifier
    """

    def __init__(self, name):
        super().__init__("Unable to find the operating system group identified as '%s'" % name)
