from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import StringQueryFilter, \
    OrQueryFilter


class ComplexInterval:
    """
    Represents a complex date-time interval to use to search the records using the date-time criterion
    """

    _timestamps = None
    _infinity_included = None

    def __init__(self, low, high, contains=True):
        """
        Initializes the complex interval

        :param low: the lower bound that equals to datetime instance or -infinity if there is no lower borders
        :param high:  the higher bound that equals to datetime instance or +infinity if there is no higher borders
        :param contains: True if interval includes all values between the lower and the higher bounds,
            False if the interval contains all values except those between the lower and the higher bounds,
        """
        if low == -float('inf'):
            if high == -float('inf'):
                self._timestamps = list()
                self._infinity_included = not contains
            elif high == float('inf'):
                self._timestamps = list()
                self._infinity_included = contains
            else:
                self._timestamps = [high]
                self._infinity_included = contains
        elif low == float('inf'):
            if high == float('inf'):
                self._timestamps = list()
                self._infinity_included = not contains
            else:
                raise ValueError("Bad interval")
        else:
            if high == -float('inf'):
                raise ValueError("Bad interval")
            elif high == float('inf'):
                self._timestamps = [low]
                self._infinity_included = not contains
            elif high >= low:
                self._timestamps = [low, high]
                self._infinity_included = not contains
            else:
                raise ValueError("Bad interval")

    @property
    def timestamps(self):
        """
        List of all timestamps related to the interval
        """
        return self._timestamps

    @property
    def infinity_included(self):
        """
        True if -infinity is included into the interval, False otherwise
        """
        return self._infinity_included

    def __contains__(self, item):
        """
        Returns true if the item contains in the complex interval

        :param item: the item to check
        :return: True if the item contains, False otherwise
        """
        if item is None:
            raise ValueError("Can check whether None contains")
        contains = self._infinity_included
        for current_item in self._timestamps:
            if item < current_item or (item == current_item and contains):
                break
            if item == current_item and not contains:
                contains = True
                break
            if item > current_item:
                contains = not contains
        return contains

    def __and__(self, other):
        """
        Returns the interval that contains both points from the interval 1 and points from the interval 2

        :param other: the other ComplexInterval to check
        :return: the operation result
        """
        timestamps1 = self.timestamps
        timestamps2 = other.timestamps
        sign1 = self.infinity_included
        sign2 = other.infinity_included
        sign = initial_sign = sign1 and sign2
        result_timestamps = list()
        while len(timestamps1) > 0 or len(timestamps2) > 0:
            t1 = timestamps1[0] if len(timestamps1) > 0 else None
            t2 = timestamps2[0] if len(timestamps2) > 0 else None
            previous_sign = sign
            if t2 is None or (t1 is not None and t1 < t2):
                sign1 = not sign1
                sign = sign1 and sign2
                if sign != previous_sign:
                    result_timestamps.append(t1)
                timestamps1 = timestamps1[1:]
            elif t1 is None or (t2 is not None and t1 > t2):
                sign2 = not sign2
                sign = sign1 and sign2
                if sign != previous_sign:
                    result_timestamps.append(t2)
                timestamps2 = timestamps2[1:]
            else:  # t1 == t2
                sign1 = not sign1
                sign2 = not sign2
                sign = sign1 and sign2
                if not sign and not previous_sign:
                    result_timestamps.append(t1)
                    result_timestamps.append(t2)
                elif sign or previous_sign:
                    result_timestamps.append(t1)
                timestamps1 = timestamps1[1:]
                timestamps2 = timestamps2[1:]
        interval = ComplexInterval(-float('inf'), -float('inf'))
        interval._infinity_included = initial_sign
        interval._timestamps = result_timestamps
        return interval

    def __or__(self, other):
        """
        Returns the interval that contains either points from the interval1 or points from the interval2

        :param other: the interval 2
        :return: the operation result
        """
        timestamps1 = self.timestamps
        timestamps2 = other.timestamps
        sign1 = self.infinity_included
        sign2 = other.infinity_included
        initial_sign = sign = sign1 or sign2
        result_timestamps = list()
        while len(timestamps1) > 0 or len(timestamps2) > 0:
            t1 = timestamps1[0] if len(timestamps1) > 0 else None
            t2 = timestamps2[0] if len(timestamps2) > 0 else None
            previous_sign = sign
            if t2 is None or (t1 is not None and t1 < t2):
                sign1 = not sign1
                sign = sign1 or sign2
                if sign != previous_sign:
                    result_timestamps.append(t1)
                timestamps1 = timestamps1[1:]
            elif t1 is None or (t2 is not None and t1 > t2):
                sign2 = not sign2
                sign = sign1 or sign2
                if sign != previous_sign:
                    result_timestamps.append(t2)
                timestamps2 = timestamps2[1:]
            else:  # t1 == t2
                sign1 = not sign1
                sign2 = not sign2
                sign = sign1 or sign2
                if sign != previous_sign:
                    result_timestamps.append(t1)
                timestamps1 = timestamps1[1:]
                timestamps2 = timestamps2[1:]
        interval = ComplexInterval(-float('inf'), -float('inf'))
        interval._infinity_included = initial_sign
        interval._timestamps = result_timestamps
        return interval

    def to_sql(self, column_name, less_transform_function, high_transform_function):
        """
        Transforms the datetime field to the query filter

        :return: the QueryFilter instance
        """
        if len(self.timestamps) == 0:
            if self.infinity_included:
                query_filter = StringQueryFilter(column_name + " IS NOT NULL")
            else:
                query_filter = StringQueryFilter("1 = 0")
        else:
            if self.infinity_included:
                query_filter = StringQueryFilter(column_name + " <= %s",
                                                 less_transform_function(self.timestamps[0]))
                idx = 1
            else:
                query_filter = OrQueryFilter()
                idx = 0
            while idx < len(self.timestamps):
                if idx < len(self.timestamps) - 1:
                    query_filter |= (
                        StringQueryFilter(column_name + " >= %s", high_transform_function(self.timestamps[idx])) &
                        StringQueryFilter(column_name + " <= %s", less_transform_function(self.timestamps[idx+1]))
                    )
                    idx += 2
                else:
                    query_filter |= \
                        StringQueryFilter(column_name + " >= %s", high_transform_function(self.timestamps[idx]))
                    idx += 1
        return query_filter
