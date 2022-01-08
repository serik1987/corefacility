from core.entity.group import Group
from core.entity.user import User

from .entity_set_object import EntitySetObject
from .user_set_object import UserSetObject


class GroupSetObject(EntitySetObject):
    """
    Defines five arbitrary user groups and allows search among them
    """

    MIN_USER_LENGTH = 10
    """ only user objects containing at least 10 users were allowed """

    __user_set_object = None
    """ To create the user group we need a proper user. This function will create such a proper user. """

    _entity_class = Group
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    def __init__(self, user_set_object: UserSetObject, _entity_list=None):
        """
        Initializes the group set object

        :param user_set_object: To create the user group we need a proper user. This property defines which
        users shall be taken (only user objects containing at least 10 users were allowed)
        """
        self.__user_set_object = user_set_object
        if len(self.__user_set_object) < self.MIN_USER_LENGTH:
            raise ValueError("Only user objects containing at least %s users were allowed" % self.MIN_USER_LENGTH)
        super().__init__(_entity_list)
        if _entity_list is None:
            self.initialize_connections()

    @property
    def user_set_object(self):
        return self.__user_set_object

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        return [
            dict(name="Сёстры Райт", governor=self.__user_set_object[1]),
            dict(name="Своеобразные", governor=self.__user_set_object[3]),
            dict(name="Управляемый хаос", governor=self.__user_set_object[4]),
            dict(name="Изгибно-крутильный флаттер", governor=self.__user_set_object[7]),
            dict(name="Революция сознания", governor=self.__user_set_object[7])
        ]

    def initialize_connections(self):
        self[0].users.add(self.__user_set_object[0])
        self[0].users.add(self.__user_set_object[2])
        self[1].users.add(self.__user_set_object[0])
        self[1].users.add(self.__user_set_object[2])
        self[1].users.add(self.__user_set_object[4])
        self[2].users.add(self.__user_set_object[3])
        self[2].users.add(self.__user_set_object[5])
        self[2].users.add(self.__user_set_object[6])
        self[3].users.add(self.__user_set_object[5])
        self[3].users.add(self.__user_set_object[6])
        self[3].users.add(self.__user_set_object[8])
        self[4].users.add(self.__user_set_object[6])
        self[4].users.add(self.__user_set_object[8])
        self[4].users.add(self.__user_set_object[9])

    def clone(self):
        group_set_object = GroupSetObject(self.__user_set_object, _entity_list=list(self._entities))
        return group_set_object

    def sort(self):
        self._entities = sorted(self._entities, key=lambda group: group.name)

    def filter_by_name(self, search_string):
        """
        Filters the objects by name

        :param search_string: a part of a group name
        :return: nothing
        """
        if search_string is not None and search_string != "":
            self._entities = list(filter(lambda group: group.name.startswith(search_string), self._entities))

    def filter_by_user(self, user):
        """
        Filters the object by the containing user

        :param user: the user to search
        :return: nothing
        """
        if isinstance(user, User):
            self._entities = list(filter(lambda group: group.users.exists(user), self._entities))
