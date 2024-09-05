from ru.ihna.kozhukhov.core_application.entity.fields.entity_field import EntityField
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import (
    EntityFieldInvalid,
    EntityFieldRequiredException
)


class RecordTypeField(EntityField):
    """
    The field stores different types of the record field
    """

    def __init__(self, description=None):
        """
        Constructor arguments:

        :param description: a human-readable description of the field
        """
        super().__init__(list, description=description)

    def proofread(self, value):
        """
        Proofreads the entity value. The method is called when the entity gets the field value to the user.
        Such value passes to the user itself who in turn proofreads such value

        :param value: the value stored in the entity as defined by one of the entity providers
        :return: the value given to the user
        """
        return list(value)  # the field can't be unsanctionally changed by call of the value methods

    def correct(self, value):
        """
        Corrects the value before the user sets it to the entity field.

        :param value: the value that user wants to set
        :return: Actual value set to the entity
        """
        if value is None:
            raise EntityFieldRequiredException('record_type')
        if isinstance(value, list):
            raw_value = value
        else:
            raw_value = [value]
        raw_value = set(raw_value)
        for value_item in raw_value:
            if not isinstance(value_item, LabjournalRecordType):
                raise EntityFieldInvalid('')
        return list(raw_value)
