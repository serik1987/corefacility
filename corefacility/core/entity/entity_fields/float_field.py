from .entity_field import EntityField


class FloatField(EntityField):
    """
    The field is used for representing floating point numbers
    """

    _min_value_included = None
    _max_value_included = None

    def __init__(self, min_value=None, max_value=None, min_value_included=False, max_value_included=False,
                 description=None):
        """
        Initializes the field

        :param min_value: minimum value
        :param max_value: maximum value
        :param min_value_included: True if minimum value is allowed to be included into the possible range
        :param max_value_included: True if maximum value is allowed to be included into the possible range
        :param description: the field description
        """
        super().__init__(float, min_value=min_value, max_value=max_value, description=description)
        self._min_value_included = min_value_included
        self._max_value_included = max_value_included

    def correct(self, value):
        raw_value = super().correct(value)
        if self._min_value is not None and value == self._min_value and not self._min_value_included:
            raise ValueError("The following value is not valid: %f" % value)
        if self._max_value is not None and value == self._max_value and not self._max_value_included:
            raise ValueError("The following value is not valid: %f" % value)
        return raw_value
