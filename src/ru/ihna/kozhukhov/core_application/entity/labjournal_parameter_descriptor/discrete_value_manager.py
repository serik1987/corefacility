import re

from ru.ihna.kozhukhov.core_application.entity.field_managers.entity_value_manager import EntityValueManager
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import \
    EntityOperationNotPermitted, EntityFieldInvalid
from ru.ihna.kozhukhov.core_application.models import LabjournalParameterAvailableValue

from .exceptions import DuplicatedValueException


class DiscreteValueManager(EntityValueManager):
    """
    Manages list of values for the DiscreteParameterDescriptor
    """

    entity_alias_pattern = re.compile(r'^[A-Za-z0-9.\-_]+$')
    entity_alias_max_chars = 256
    entity_description_max_chars = 256

    def add(self, alias, description):
        """
        Adds a possible value to the list of possible values

        :param alias: string ID of the possible value
        :param description: Human-readable description of the possible value
        :return: a dictionary containing the following fields
            'id' digital ID of the possible value
            'alias': string ID of the possible value
            'description': human-readable description of the possible value
        """
        if self._entity.state in ['creating', 'deleted']:
            raise EntityOperationNotPermitted("To add possible value the parameter descriptor must be created in "
                                              "all of its external sources")
        if not isinstance(alias, str) or not self.entity_alias_pattern.match(alias) or \
                len(alias) > self.entity_alias_max_chars:
            raise EntityFieldInvalid("values.alias")
        if not isinstance(description, str) or description == "" or \
                len(description) > self.entity_description_max_chars:
            raise EntityFieldInvalid("values.description")
        if self._entity._values is None:
            self._entity._values = list()
        for value in self._entity._values:
            if value['alias'] == alias:
                raise DuplicatedValueException()
        table_row = LabjournalParameterAvailableValue(
            alias=alias,
            description=description,
            descriptor_id=self._entity.id,
        )
        table_row.save()
        self._entity._values.append(dict(
            id=table_row.id,
            alias=alias,
            description=description,
        ))

    def remove(self, value):
        """
        Removes a possible value from the list of possible values

        :param value: identifier or string ID of the value to remove
        """
        if self._entity.state in ['creating', 'deleted']:
            raise EntityOperationNotPermitted("To add possible value the parameter descriptor must be created in "
                                              "all of its external sources")
        value_info = None
        value_index = None
        if self._entity._values is not None:
            local_index = 0
            for value_info_local in self._entity._values:
                if (isinstance(value, int) and value_info_local['id'] == value) or \
                        (isinstance(value, str) and value_info_local['alias'] == value):
                    value_index = local_index
                    value_info = value_info_local
                    break
                local_index += 1
        if value_index is None or value_info is None:
            raise EntityOperationNotPermitted("The possible value '%s' was not found" % value)
        table_row = LabjournalParameterAvailableValue.objects.get(id=value_info['id'])
        table_row.delete()
        del self._entity._values[value_index]

    def __len__(self):
        """
        Counts all possible values

        :return: total number of all possible values
        """
        value_number = 0
        if self._entity._values is not None:
            value_number = len(self._entity._values)
        return value_number

    def __iter__(self):
        """
        Iterates over all possible values

        :return: an iterable object that allows such an iteration
        """
        if self._entity._values is not None:
            for possible_value in self._entity._values:
                yield possible_value
