import re
from datetime import timedelta
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.dateparse import parse_duration
from rest_framework.fields import BooleanField
from rest_framework.exceptions import NotFound, ValidationError, ParseError
from rest_framework import status

from ru.ihna.kozhukhov.core_application import App
from ru.ihna.kozhukhov.core_application.utils import LabjournalCache
from ru.ihna.kozhukhov.core_application.generic_views import EntityListView
from ru.ihna.kozhukhov.core_application.serializers.labjournal import RecordSerializer
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RecordSet, RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.complex_interval import ComplexInterval
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType, LabjournalFieldType
from ru.ihna.kozhukhov.core_application.exceptions.api_exceptions import EntitySetIsEmpty

date_from_filter_function = EntityListView.date_filter_function('date_from')
date_to_filter_function = EntityListView.date_filter_function('date_to')


class BaseCategoryView(EntityListView):
    """
    This is the base class for category operation (viewing, exporting, adding records, batch processing).
    """

    MAX_HASHTAG_NUMBER = 20
    """ Maximum number of hashtags to use """

    custom_parameter_template = re.compile(r'^custom_(.+)$')
    """ All query parameters that match this template will be treated as custom parameters """

    application = App()
    """ The application related to the view """

    data_gathering_way = 'uploading'
    """ A way the user can gather the data """

    list_serializer_class = RecordSerializer
    """ The class is responsible for serialization / deserialization of the record """

    detail_serializer_class = RecordSerializer
    """ The class is responsible for serialization / deserialization of the record """

    entity_set_class = RecordSet
    """ Class that represents list of all entities """

    list_filters = {
        'name': EntityListView.standard_filter_function('name', str),
    }
    """ Filters for the entity list """

    cache = LabjournalCache()
    """ Allows to control the size of the labjournal cache """

    parent_category_access = None
    """
    Type of the parent category access:
    'root_only' access to the root category;
    'by_id' access the category by ID;
    'by_path' access to the category by its path
    """

    _date_filter = None
    """ Total date filter, is applicable """

    __bad_custom_parameters_exist = None
    """ True if at leat one bad custom parameter exists, False if bad custom parameters were not found """

    _search_on_relative_date_when_reference_date_is_none = False
    """
    If False, the view will throw the ValidationError when either date_from_relative or date_to_relative filters is ON
    and parent category doesn't have its own datetime.
    If True, the view will return an empty record set in this case
    """

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)
        self.cache.flush()
        record_set = RecordSet()
        if self.parent_category_access is None or self.parent_category_access == 'root_only':
            request.parent_category = RootCategoryRecord(project=request.project)
        elif self.parent_category_access == 'by_id':
            parent_category = self.get_entity_or_404(record_set, kwargs['category_id'])
            if parent_category.project.id != request.project.id:
                raise NotFound()
            request.parent_category = parent_category
        elif self.parent_category_access == 'by_path':
            request.parent_category = \
                self.get_entity_or_404(record_set, (request.project, kwargs['category_path']))
        else:
            raise ValueError("Value of the initkwarg parent_category_access='%s' is incorrect or unsupported"
                             % self.parent_category_access)
        if request.parent_category.type != LabjournalRecordType.category:
            raise ParseError()

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (E.g. return a list of items that is specific to the user)
        """
        record_set = RecordSet()
        record_set.parent_category = self.request.parent_category
        record_set.user = self.request.user
        return record_set

    def filter_queryset(self, record_set):
        """
        Provides filtration of the record list according to one or several criteria given inside the request
        query parameters.

        :param record_set: The RecordSet object that allows to query for the database for iterating over all records
        :return: Any container that contains records or no elements and supports counting, iterations, slicing and
            indexation (mostly, this is RecordSet object with all filters properly adjusted; more seldom this is
            list object with no elements)
        """
        record_set = super().filter_queryset(record_set)
        self._date_filter = None
        try:
            if 'date_from' in self.request.query_params or 'date_to' in self.request.query_params:
                self._apply_date_filter(
                    date_from_filter_function(self.request.query_params),
                    date_to_filter_function(self.request.query_params)
                )
            if 'type' in self.request.query_params:
                self._apply_type_filter(record_set)
            if 'hashtags' in self.request.query_params and \
                    'date_from_hashtags' not in self.request.query_params and \
                    'date_to_hashtags' not in self.request.query_params:
                self._apply_hashtags_filter(record_set)
            if 'hashtags' in self.request.query_params and \
                    (
                            'date_from_hashtags' in self.request.query_params or
                            'date_to_hashtags' in self.request.query_params
                    ):
                self._apply_hashtag_date_from_filter()
            if 'date_from_relative' in self.request.query_params or 'date_to_relative' in self.request.query_params:
                self._apply_relative_date_filter()
            self._apply_custom_parameter_filter(record_set)
            if self._date_filter is not None:
                record_set.datetime = self._date_filter
        except EntitySetIsEmpty:
            record_set = list()
        return record_set

    def _apply_date_filter(self, date_from, date_to):
        """
        Passes only records that lies between two specific absolute dates and times

        :param date_from: The passed records shall have dates not earlier than this date. None if not applicable.
        :param date_to: The passed records shall have not later than this date. None if not applicable.
        """
        if date_from is not None and date_to is not None:
            try:
                local_date_filter = ComplexInterval(date_from, date_to)
            except ValueError:
                raise EntitySetIsEmpty()
        elif date_from is not None and date_to is None:
            local_date_filter = ComplexInterval(date_from, float('inf'))
        elif date_from is None and date_to is not None:
            local_date_filter = ComplexInterval(-float('inf'), date_to)
        else:
            raise ValueError("Bad method usage.")
        if self._date_filter is not None and local_date_filter is not None:
            self._date_filter &= local_date_filter
        elif self._date_filter is None and local_date_filter is not None:
            self._date_filter = local_date_filter

    def _apply_type_filter(self, record_set):
        """
        Filters the record set by types of the record

        :param record_set: the record set to filter
        """
        if len(self.request.query_params['type']) > 0:
            type_list = self.request.query_params['type'].split(',')
            try:
                type_list = [getattr(LabjournalRecordType, type_name) for type_name in type_list]
            except AttributeError:
                raise ValidationError("Bad value of 'type' query parameter")
            record_set.types = type_list
        else:
            raise EntitySetIsEmpty()

    def _apply_hashtags_filter(self, record_set):
        """
        Passes only such records that contain specific hashtags

        :param record_set: a record set which filters should be adjusted
        """
        hashtag_logic = self.__get_logic_type('hashtag_logic')
        hashtag_list_raw = self.request.query_params['hashtags']
        if len(hashtag_list_raw) == 0:
            raise EntitySetIsEmpty()
        hashtag_list_str = hashtag_list_raw.split(',')
        try:
            hashtag_list = [int(hashtag_id) for hashtag_id in hashtag_list_str]
        except ValueError:  # At least one hashtag from the hashtag list is invalid
            if hashtag_logic == RecordSet.LogicType.AND:
                raise EntitySetIsEmpty()
            if len(hashtag_list_str) > self.MAX_HASHTAG_NUMBER:
                raise ValidationError({'hashtag_list': "At least one hashtag from the list is invalid"})
            hashtag_list = list()
            for hashtag_item in hashtag_list_str:
                try:
                    hashtag_list.append(int(hashtag_item))
                except ValueError:
                    pass
        record_set.hashtags = hashtag_list
        record_set.hashtag_logic = hashtag_logic

    def _apply_hashtag_date_from_filter(self):
        """
        Passes only such records that are located inside given intervals relatively records with given hashtags
        """
        duration_from, duration_to = self.__parse_durations('date_from_hashtags', 'date_to_hashtags')
        auxiliary_record_set = self.get_queryset()
        try:
            self._apply_hashtags_filter(auxiliary_record_set)
            reference_record_size = len(auxiliary_record_set)
        except EntitySetIsEmpty:
            reference_record_size = 0
        if reference_record_size == 0:
            if duration_to is not None:
                raise EntitySetIsEmpty()
            if self._date_filter is None:
                self._date_filter = ComplexInterval(-float('inf'), float('inf'))
                # which means that we must pass all records which datetime is not None
            return
        if reference_record_size > settings.LABJOURNAL_MAXIMUM_TAGGED_RECORDS:
            raise ValidationError({'hashtag_list': _("Too many tagged records.")})
        duration_from_interval, duration_to_interval = self.__calculate_durations_from_record_set(
            auxiliary_record_set,
            duration_from,
            duration_to,
        )
        if duration_from_interval is None and duration_to_interval is None:
            if duration_to is not None:
                raise EntitySetIsEmpty()
            if duration_to is not None:
                self._date_filter = ComplexInterval(-float('inf'), float('inf'))
                # which means that we must pass all records which datetime is not None
            return
        elif duration_from_interval is None and duration_to_interval is not None:
            local_date_filter = duration_to_interval
        elif duration_from_interval is not None and duration_to_interval is None:
            local_date_filter = duration_from_interval
        else:
            local_date_filter = duration_from_interval & duration_to_interval
        if self._date_filter is None:
            self._date_filter = local_date_filter
        else:
            self._date_filter &= local_date_filter

    def _apply_custom_parameter_filter(self, record_set):
        """
        Filters the data by various custom parameters

        :param record_set: the record set to use
        """
        custom_parameters = self.__parse_custom_parameters()
        if len(custom_parameters) == 0:
            return
        self.__bad_custom_parameters_exist = False  # No bad custom parameters still found.
        descriptors = self.request.parent_category.computed_descriptors
        filter_logic = self.__get_logic_type('logic_custom')
        custom_parameters = self.__filter_nonexistent_parameters(descriptors, custom_parameters)
        custom_parameters = self.__convert_parameter_values(descriptors, custom_parameters)
        if self.__bad_custom_parameters_exist and \
                (len(custom_parameters) == 0 or filter_logic == RecordSet.LogicType.AND):
            # len(custom_parameters) == 0 means that filter parameters contain only lie
            # filter_logic == RecordSet.LogicType.AND means that conjunction with lie always gives lie
            raise EntitySetIsEmpty()
        custom_parameters['_logic'] = filter_logic
        record_set.custom_parameters = custom_parameters

    def _apply_relative_date_filter(self):
        """
        Passes only such records which dates starts from given values relatively to the category start date
        """
        duration_from, duration_to = self.__parse_durations('date_from_relative', 'date_to_relative')
        reference_date = self.request.parent_category.datetime
        if reference_date is None:
            if self._search_on_relative_date_when_reference_date_is_none:
                raise EntitySetIsEmpty()
            else:
                raise ValidationError({
                    'relative_date_from': _("The relative date search can't be applied for a given category"),
                    'relative_date_to': _("The relative date search can't be applied for a given category"),
                })
        self._apply_date_filter(
            reference_date + duration_from if duration_from is not None else None,
            reference_date + duration_to if duration_to is not None else None,
        )

    def __parse_durations(self, duration_from_query_param, duration_to_query_param):
        """
        Parses fields containing information about minimum and maximum durations.
        If duration given in the query parameters is invalid throws ValidationError.
        If duration interval is empty it throws the EntitySetIsEmpty exception.

        :param duration_from_query_param: name of a query parameter that contains minimum allowed duration
        :param duration_to_query_param: name of a query_parameter that contains maximum allowed duration
        :return: a two-item tuple
            duration_from - a datetime.timedelta object that relates to minimum allowed duration
            duration_to - a datetime.timedelta object that relates to maximum allowed duration
        """
        duration_from = self.request.query_params.get(duration_from_query_param, None)
        if duration_from is not None:
            duration_from = parse_duration(duration_from)
            if duration_from is None or duration_from < timedelta(0):
                # parse_duration always returns None is parsing is failed
                raise ValidationError({duration_from_query_param: "Invalid duration."})
        duration_to = self.request.query_params.get(duration_to_query_param, None)
        if duration_to is not None:
            duration_to = parse_duration(duration_to)
            if duration_to is None or duration_to < timedelta(0):
                # parse_duration always returns None is parsing is failed
                raise ValidationError({duration_to_query_param: "Invalid duration."})
        if duration_to is not None and duration_from is not None and duration_to < duration_from:
            raise EntitySetIsEmpty()
        return duration_from, duration_to

    def __calculate_durations_from_record_set(self, auxiliary_record_set, duration_from, duration_to):
        """
        Calculates ComplexInterval's that satisfy the following conditions:
        (1) If duration_from is set, there are no points that followed any record being inside the auxiliary_record_set
            by duration less than duration_from
        (2) If duration_to is set, for any point inside the ComplexInterval there must be at least one record inside the
            auxiliary_record that is preceded this point by the duration not greater than duration_to
        """
        duration_from_interval = None
        duration_to_interval = None
        for reference_record in auxiliary_record_set:
            if reference_record.datetime is None:
                continue
            if duration_from is not None:
                local_duration_from_interval = ComplexInterval(
                    reference_record.datetime - timedelta(seconds=1),
                    reference_record.datetime + duration_from,
                    contains=False
                )
                if duration_from_interval is None:
                    duration_from_interval = local_duration_from_interval
                else:
                    duration_from_interval &= local_duration_from_interval
            if duration_to is not None:
                local_duration_to_interval = ComplexInterval(
                    reference_record.datetime,
                    reference_record.datetime + duration_to - timedelta(seconds=1),
                    contains=True,
                )
                if duration_to_interval is None:
                    duration_to_interval = local_duration_to_interval
                else:
                    duration_to_interval |= local_duration_to_interval
        return duration_from_interval, duration_to_interval

    def __get_logic_type(self, parameter_name):
        """
        Extracts the logic type from a query parameter.
        Parameter values 'and', 'AND' relate to RecordSet.LogicType.AND.
        Parameter values 'or', 'OR' relate to RecordSet.LogicType.OR.
        If the logic type is not provided by the HTTP client,
        RecordSet.LogicType.AND will be given as default logic type

        :param parameter_name: name of the query parameter that contains information about the logic type
        :return: given logic type (a value of RecordSet.LogicType).
        """
        logic_type_raw = self.request.query_params.get(parameter_name, 'and').upper()
        try:
            logic_type = getattr(RecordSet.LogicType, logic_type_raw)
        except AttributeError:
            raise ValidationError({parameter_name: "Bad value. Valid values are 'and' or 'or'"})
        return logic_type

    def __parse_custom_parameters(self):
        """
        Selects custom parameters from the request

        :return: a dictionary custom parameter name => custom parameter value
        """
        custom_parameters = dict()
        for full_parameter_name, parameter_value in self.request.query_params.items():
            parameter_match = self.custom_parameter_template.match(full_parameter_name)
            if parameter_match is not None:
                parameter_name = parameter_match[1]
                custom_parameters[parameter_name] = parameter_value
        return custom_parameters

    def __filter_nonexistent_parameters(self, descriptors, custom_parameters):
        """
        Removes all custom parameters for which descriptors are not defined.

        :param descriptors: all computed descriptors
        :param custom_parameters: dictionary of custom parameters before removal
        :return: dictionary of custom parameters after removal
        """
        cleaned_parameters = dict()
        for parameter_name, parameter_value in custom_parameters.items():
            if parameter_name in descriptors:
                cleaned_parameters[parameter_name] = parameter_value
            else:
                self.__bad_custom_parameters_exist = True
        return cleaned_parameters

    def __convert_parameter_values(self, descriptors, custom_parameters):
        """
        Converts values of custom parameters to proper types according to the parameter specification

        :param descriptors: parameter specification given in the computed descriptors
        :param custom_parameters: custom parameters to be converted
        :return: custom parameters after conversion
        """
        converted_parameters = dict()
        for name, value in custom_parameters.items():
            descriptor = descriptors[name]
            parameter_is_bad = False
            if descriptor.type == LabjournalFieldType.boolean:
                if value in BooleanField.TRUE_VALUES:
                    value = True
                elif value in BooleanField.FALSE_VALUES:
                    value = False
                else:
                    parameter_is_bad = True
                    self.__bad_custom_parameters_exist = True
            elif descriptor.type == LabjournalFieldType.number:
                try:
                    value = float(value)
                except ValueError:
                    parameter_is_bad = True
                    self.__bad_custom_parameters_exist = True
            elif descriptor.type == LabjournalFieldType.discrete:
                value_list = [value_info['alias'] for value_info in descriptor.values]
                if value not in value_list:
                    parameter_is_bad = True
                    self.__bad_custom_parameters_exist = True
            elif descriptor.type == LabjournalFieldType.string:
                pass
            else:
                parameter_is_bad = True
                self.__bad_custom_parameters_exist = True
            if not parameter_is_bad:
                converted_parameters[name] = value
        return converted_parameters
