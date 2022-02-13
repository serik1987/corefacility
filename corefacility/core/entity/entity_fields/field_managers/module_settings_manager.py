from .entity_value_manager import EntityValueManager


class ModuleSettingsManager(EntityValueManager):
    """
    This module is used for correct setting and reading the module settings
    """

    def get(self, name, default_value=None):
        """
        Reads the module setting

        :param name: the module setting name
        :param default_value: value that shall be returned if no such module settings has been set
        :return: an actual module setting
        """
        if self._field_value is None:
            value = default_value
        elif name in self._field_value:
            value = self._field_value[name]
        else:
            value = default_value
        return value

    def set(self, name, value):
        """
        Writes the module settings. Please, try to use mainly primitive properties

        :param name: the module setting name
        :param value: the module setting value
        :return: nothing
        """
        self._field_value[name] = value
        self.entity.notify_field_changed(self.field_name)

    def __len__(self):
        """
        Defines total number of user settings

        :return: the total number of user settings
        """
        return len(self._field_value)

    def __eq__(self, other):
        """
        Compares two module settings managers for debugging purpose

        :param other: the other module settings manager
        :return: True if two module settings sets were equal, false otherwise
        """
        if not isinstance(other, ModuleSettingsManager):
            return False
        if self._field_value is None:
            return other._field_value is None
        else:
            for name, value in self._field_value.items():
                other_value = other.get(name)
                if value != other_value:
                    return False
            for name, value in self._field_value.items():
                other_value = self.get(name)
                if value != other_value:
                    return False
            return True
