from .entity_field import EntityField


class ReadOnlyField(EntityField):
    """
    Read only fields are fields where any write access is prohibited
    """

    def __init__(self, description=None, default=None):
        """
        Initializes this read-only field

        :param description: the field value to user in logging and debugging
        :param default: default field value
        """
        super().__init__(EntityField.identity, description=description, default=default)

    def correct(self, value):
        """
        Tells the user that he has not any write access to that field

        :param value: any value given to the user that is absolutely not interesting for us
        :return: nothing
        """
        raise ValueError("The writing access to this entity field is not implied")
