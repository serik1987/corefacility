class ExpectedPermission:
    """
    Provides an information about the expected permission.

    The expected permission shall be compared with the actual one.
    """

    group_id = None
    group_name = None
    level_alias = None

    def __init__(self, group_id=None, group_name=None, level_alias=None):
        """
        Creates new permission list item

        :param group_id: ID of the permitting group
        :param group_name: name of the permitting group
        :param level_alias: human-readable name of the access level
        """
        self.group_id = group_id
        self.group_name = group_name
        self.level_alias = level_alias
