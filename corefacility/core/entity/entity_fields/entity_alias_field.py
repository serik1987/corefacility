from .entity_field import EntityField


class EntityAliasField(EntityField):
    """
    Provides additional constraints for setting entity aliases: a string containing only latin letters and digits,
    underscores, dashes or dots
    """

    def __init__(self, max_length=None):
        """
        Defines the alias entity.

        :param max_length: maximum length of the entity object
        """
        super().__init__(str, min_length=1, max_length=max_length, description="Entity alias")

    def correct(self, value):
        """
        Provides additional constraints on setting the entity alias

        :param value: the alias value user wants to set
        :return: the alias value that will actually be set
        """
        raise NotImplementedError("TO-DO: implement EntityAliasField.correct")
