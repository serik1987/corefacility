from core.entity.user import User

from .entity_set_object import EntitySetObject


class UserSetObject(EntitySetObject):
    """
    Retrieves the new entity set
    """

    _entity_class = User
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    _alias_field = "login"
    """ The alias field. Override this class property is this is not true. """

    def data_provider(self):
        return [
            dict(login="user1", surname="Миронова", name="Екатерина"),
            dict(login="user2", surname="Золотова", name="Полина"),
            dict(login="user3", surname="Орехова", name="Мария"),
            dict(login="user4", surname="Павлов", name="Илья"),
            dict(login="user5", surname="Цветков", name="Леон"),
            dict(login="user6", surname="Соловьева", name="Дарья"),
            dict(login="user7", surname="Комаров", name="Артём"),
            dict(login="user8", surname="Дмитриев", name="Илья"),
            dict(login="user9", surname="Спиридонова", name="Анастасия"),
            dict(login="user10", surname="Сычёв", name="Александр"),
        ]

    def sort(self):
        """
        Sorts users in such a way as to make their order identical to another one retrieved from the database

        :return: nothing
        """
        self._entities = sorted(self._entities)

    def filter_by_is_support(self, value):
        """
        Filters the user by whether this is support user or not.

        :param value: defines whether this user is support
        :return: nothing
        """
        if value:
            self._entities = []

    def filter_by_name(self, value):
        """
        Filters the users by name

        :param value: name to filter
        :return: nothing
        """
        if value == "" or value is None:
            return
        self._entities = list(filter(
            lambda e: (e.surname is not None and e.surname.find(value) != -1) or
                      (e.name is not None and e.name.find(value) != -1) or
                      (e.login is not None and e.login.find(value) != -1),
            self._entities
        ))

    def filter_by_is_locked(self, value):
        """
        Filters by whether the user is locked

        :param value: the filter value
        :return: nothing
        """
        self._entities = list(filter(lambda user: user.is_locked == value, self._entities))

    def filter_by_group(self, group):
        """
        Filters only such users that exists in a given group

        :param group: the group that must be checked
        :return: nothing
        """
        self._entities = list(filter(lambda user: group in user.groups, self._entities))
