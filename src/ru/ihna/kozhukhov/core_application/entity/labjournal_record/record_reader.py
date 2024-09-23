from datetime import timedelta
import json
from json import JSONDecodeError
from django.conf import settings

from ru.ihna.kozhukhov.core_application.entity.readers.raw_sql_query_reader import RawSqlQueryReader
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator, time_from_db, prepare_time
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.data_source import SqlTable, Subquery
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import \
    StringQueryFilter, OrQueryFilter, SearchQueryFilter, AndQueryFilter
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType, LabjournalRecordType, \
    LabjournalFieldType

from ..labjournal_hashtags import RecordHashtag
from .record_provider import RecordProvider


class RecordReader(RawSqlQueryReader):
    """
    Reads labjournal records from the database
    """

    _entity_provider = RecordProvider()
    _query_debug = False

    _lookup_table_name = 'record'
    """
    Change this property if get() method will give you something like 'column ... is ambiguous'.
    This will make get() method to add 'WHERE tbl_name.id=%s' instead of 'WHERE id=%s'
    """

    _user_context = None
    """ The user context that will be automatically put to all assigned entities """

    _hashtag_filter = None
    """ Hashtag filter to apply """

    _hashtag_logic_filter = None
    """ Logic of the hashtag filter to apply """

    _parent_category = None
    """
    If parent_category filter is selected, the property equals to the value of the parent category selected by the user.
    Otherwise, the property is None.
    """

    def initialize_query_builder(self):
        """
        This function shall call certain methods for the query builder to make
        it to generate proper queries given that no external filters applied

        :return: nothing
        """
        self.items_builder \
            .add_select_expression('record.type') \
            .add_select_expression('record.id') \
            .add_select_expression('record.project_id') \
            .add_select_expression('project.alias') \
            .add_select_expression('project.root_group_id') \
            .add_select_expression('record.parent_category_id') \
            .add_select_expression('parent_category.datetime') \
            .add_select_expression('parent_category.finish_time') \
            .add_select_expression('record.level') \
            .add_select_expression('record.alias') \
            .add_select_expression('record.datetime') \
            .add_select_expression('record.comments') \
            .add_select_expression('record.finish_time') \
            .add_select_expression('record.base_directory') \
            .add_select_expression('record.name') \
            .add_select_expression('record.custom_parameters') \
            .add_select_expression(self.items_builder.json_object_aggregation('hashtag.id', 'hashtag.description')) \
            .add_data_source(SqlTable('core_application_labjournalrecord', 'record')) \
            .add_order_term('record.datetime',
                            direction=self.items_builder.ASC,
                            null_direction=self.items_builder.NULLS_FIRST)

        self.items_builder.data_source.add_join(
            self.items_builder.JoinType.LEFT,
            SqlTable('core_application_labjournalhashtagrecord', 'hashtag_connector'),
            "ON (hashtag_connector.record_id = record.id)"
        )
        self.items_builder.data_source.add_join(
            self.items_builder.JoinType.LEFT,
            SqlTable("core_application_labjournalhashtag", 'hashtag'),
            "ON (hashtag.id = hashtag_connector.hashtag_id)"
        )
        self.items_builder.add_group_term("record.id")

        self.count_builder \
            .add_select_expression(self.count_builder.select_total_count('record.id', distinct=True)) \
            .add_data_source(SqlTable('core_application_labjournalrecord', 'record'))

        for builder in self.items_builder, self.count_builder:
            builder.data_source \
                .add_join(
                    self.items_builder.JoinType.INNER,
                    SqlTable('core_application_project', 'project'),
                    "ON (project.id = record.project_id)"
                ) \
                .add_join(
                    self.items_builder.JoinType.LEFT,
                    SqlTable('core_application_labjournalrecord', 'parent_category'),
                    "ON (parent_category.id = record.parent_category_id)"
                )

        self._user_context = None

    def apply_parent_category_filter(self, parent_category):
        """
        Applies the parent category filter

        :param parent_category: the parent category to apply
        """
        self._parent_category = parent_category
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= \
                StringQueryFilter("record.project_id=%s", parent_category.project.id)
            if parent_category.is_root_record:
                builder.main_filter &= StringQueryFilter("record.parent_category_id IS NULL")
            else:
                builder.main_filter &= \
                    StringQueryFilter("record.parent_category_id=%s", parent_category.id)

    def apply_alias_filter(self, alias):
        """
        Remains only records with a particular alias

        :param alias: the alias filter to apply
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("record.alias=%s", alias)

    def apply_type_filter(self, record_type):
        """
        Remains only records with a given record type

        :param record_type: the type filter to apply
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("record.type=%s", str(record_type))

    def apply_user_filter(self, user):
        """
        Adds the user context to the record
        """
        self.items_builder.data_source.add_join(
            self.items_builder.JoinType.LEFT,
            SqlTable('core_application_labjournalcheckedrecord', 'check_info'),
            "ON (check_info.record_id = record.id AND check_info.user_id=%d)" % int(user.id)
            # I think that variable -> int(variable) prevents any SQL injections for this in Python
            # int("0; DROP TABLE students;") throws ValueError according to the Python syntax specifications
        )
        self.items_builder.add_select_expression('check_info.user_id')
        self._user_context = user

    def apply_datetime_filter(self, interval):
        """
        Passes only records which datetime field is within a given interval

        :param interval: a ComplexInterval instance
        """
        less_transform_function = prepare_time
        high_transform_function = lambda t: prepare_time(t - timedelta(seconds=1))
        query_filter = interval.to_sql('record.datetime', less_transform_function, high_transform_function)
        if query_filter is not None:
            self.items_builder.main_filter &= query_filter
            self.count_builder.main_filter &= query_filter

    def apply_types_filter(self, types):
        """
        Passes only records having certain types

        :param types: an iterable object containing available types
        """
        for record_type in types:
            if not isinstance(record_type, LabjournalRecordType):
                raise ValueError("The type is not a valid instance LabjournalRecordType")
                # Ensures no SQL injections
        if len(types) > 0:
            query = OrQueryFilter(
                *[StringQueryFilter("record.type = '%s'" % str(record_type)) for record_type in types]
            )
            self.items_builder.main_filter &= query
            self.count_builder.main_filter &= query
        else:
            self.items_builder.main_filter &= StringQueryFilter("1 = 0")
            self.count_builder.main_filter &= StringQueryFilter("1 = 0")

    def apply_name_filter(self, name):
        """
        Passes only records which name starts from a given line

        :param name: the name to apply
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= SearchQueryFilter("record.name", name, must_start=True)

    def apply_hashtags_filter(self, hashtags):
        """
        Passes only records containing given hashtags

        :param hashtags: list of hashtag entities or hashtag IDs
        """
        hashtags = [hashtag.id if isinstance(hashtag, RecordHashtag) else hashtag for hashtag in hashtags]
        if self._hashtag_logic_filter is not None:
            self._apply_custom_hashtag_filter(hashtags, self._hashtag_logic_filter)
        else:
            self._hashtag_filter = hashtags

    def apply_hashtag_logic_filter(self, hashtag_logic):
        """
        Defines the logic that the hashtags should be applied

        :param hashtag_logic: one out of the predefined hashtag logic
        """
        if self._hashtag_filter is not None:
            self._apply_custom_hashtag_filter(self._hashtag_filter, hashtag_logic)
        else:
            self._hashtag_logic_filter = hashtag_logic

    def _apply_custom_hashtag_filter(self, hashtag_id_list, hashtag_logic):
        """
        Applies a custom hashtag filter

        :param hashtag_id_list: Records that have hashtags with IDs in the list will be remained
        :param hashtag_logic: how presence of hashtags shall be considered
            RecordSet.LogicType.AND - a record shall contain all hashtags present in the hashtag_id_list to remain it
            RecordSet.LogicType.OR - a record shall contain at least one hashtag present in the hashtag_id_list
                to remain it
        """
        if len(hashtag_id_list) > 0:
            child_entity_filter_options = {
                'data_source': 'core_application_labjournalhashtagrecord',
                'count_column': 'hashtag_id',
                'child_values': hashtag_id_list,
                'value_to_filter_converter': lambda hashtag_id: \
                    StringQueryFilter("core_application_labjournalhashtagrecord.hashtag_id=%s", hashtag_id),
                'subquery_alias': 'hashtag_stats',
            }
            if hashtag_logic.value == "and":
                self.apply_child_entity_and_filter(**child_entity_filter_options)
            elif hashtag_logic.value == "or":
                self.apply_child_entity_or_filter(**child_entity_filter_options)
            else:
                print(hashtag_logic)
                raise ValueError("Unsupported hashtag_logic")

    def apply_custom_parameters_filter(self, custom_parameters):
        """
        Remains only such records that contains special values of custom parameters

        :param custom_parameters: a dictionary identifier => value that defines such special values, where
            identifier is an identifier of the custom parameter and value is its value
        """
        if self._parent_category is None:
            raise ValueError("Please, select a parent category to successively apply this filter")
        if len(custom_parameters) > 0:
            computed_descriptors = self._parent_category.computed_descriptors
            logic = custom_parameters['_logic']
            derived_custom_parameters = dict()
            for identifier, value in custom_parameters.items():
                if identifier in computed_descriptors:
                    descriptor = computed_descriptors[identifier]
                    if descriptor.type == LabjournalFieldType.boolean:
                        value = float(value)
                    derived_custom_parameters[descriptor.id] = value
            filter_options = {
                'data_source': "core_application_labjournalparametervalue",
                'count_column': "descriptor_id",
                'child_values': derived_custom_parameters.items(),
                'value_to_filter_converter': self._define_filter_for_value,
                'subquery_alias': 'param_stats',
            }
            if logic.value == 'and':
                self.apply_child_entity_and_filter(**filter_options)
            elif logic.value == 'or':
                self.apply_child_entity_or_filter(**filter_options)

    def _define_filter_for_value(self, combined_value):
        """
        Defines an SQL filter for a given pair (parameter ID, parameter value)

        :param combined_value: the value itself
        """
        param_id, param_value = combined_value
        query_filter = StringQueryFilter("core_application_labjournalparametervalue.descriptor_id=%s", param_id)
        if isinstance(param_value, str):
            query_filter &= StringQueryFilter("core_application_labjournalparametervalue.string_value=%s", param_value)
        elif isinstance(param_value, float):
            query_filter &= StringQueryFilter("core_application_labjournalparametervalue.float_value=%s", param_value)
        else:
            raise ValueError("Unsupported type of the parameter value")
        return query_filter

    def apply_child_entity_and_filter(self,
                                  data_source=None,
                                  count_column=None,
                                  child_values=None,
                                  value_to_filter_converter=None,
                                  subquery_alias=None,
                                  ):
        """
        Passes only such records that have child entities satisfying the following condition: all entities within a
        given entity list are child entities of a given record.

        IMPORTANT NOTE!
        All arguments below are mandatory. The method doesn't test them against SQL-injection. However, the
        value_to_filter_converter shall test each of child_values against SQL-injection.

        :param data_source: a data source (a subquery or SQL table) where information about child entity exists.
            The data_source shall have a record_id column that is used to join the child entity to its parent record.
        :param count_column: a column that is used to distinguish rows that are related to different child entities
            inside the source data (usually, a column that contains primary key for a child entity)
        :param child_values: List or other iterable object of values that shall be consecutively passed to the
            filters. The record will pass through the filter if all entities which values are mentioned here
            are present among the child entities. The 'value_to_filter_converter' argument defines what kind of
            values we need
        :param value_to_filter_converter: The value-to-filter converter is a special function or another callable object
            that takes just one argument - value of a child entity from the 'child_values' array (see above). Its
            output should be QueryFilter that will  be inserted into WHERE condition. Such a filter should select
            only such rows from the 'data_source' (see above) that contains information about a child entity that have
            a value given by the argument to this special function
        :param subquery_alias: Selection of proper rows from an SQL table mentioned in the 'data_source' (see above)
            will be putted into a special subquery which resultant table will be joined to the original table mentioned
            in self.items_builder or self.count_builder. Such a special subquery shall have its alias. The alias should
            be given here, in this argument
        """
        subquery_builder = settings.QUERY_BUILDER_CLASS()
        subquery_builder \
            .add_select_expression("record_id") \
            .add_select_expression(subquery_builder.select_total_count(count_column), alias="entity_count") \
            .add_data_source(data_source) \
            .set_main_filter(OrQueryFilter(*[value_to_filter_converter(value) for value in child_values])) \
            .add_group_term("record_id")

        for builder in self.items_builder, self.count_builder:
            builder.data_source.add_join(
                builder.JoinType.INNER,
                Subquery(subquery_builder, subquery_alias),
                "ON (%s.record_id = record.id)" % subquery_alias
            )
            builder.main_filter &= StringQueryFilter("%s.entity_count=%%s" % subquery_alias, len(child_values))

    def apply_child_entity_or_filter(self,
                                     data_source=None,
                                     child_values=None,
                                     value_to_filter_converter=None,
                                     **kwargs
                                     ):
        """
        Passes only such records that have child entities satisfying the following condition: at least one entity within
        a given entity list is a child entity of a given record.

        IMPORTANT NOTE!
        All arguments below are mandatory. The method doesn't test them against SQL-injection. However, the
        value_to_filter_converter shall test each of child_values against SQL-injection.

        :param data_source: a data source (a subquery or SQL table) where information about child entity exists.
            The data_source shall have a record_id column that is used to join the child entity to its parent record.
        :param child_values: List or other iterable object of values that shall be consecutively passed to the
            filters. The record will pass through the filter if at least one entity inside the present list is present
            among the child entities of the record. The 'value_to_filter_converter' argument defines what kind of
            values we need
        :param value_to_filter_converter: The value-to-filter converter is a special function or another callable object
            that takes just one argument - value of a child entity from the 'child_values' array (see above). Its
            output should be QueryFilter that will  be inserted into WHERE condition. Such a filter should select
            only such rows from the 'data_source' (see above) that contains information about a child entity that have
            a value given by the argument to this special function
        :param kwargs: useless. The field has left just for compatibility reasons
        """
        child_entity_or_filter = OrQueryFilter(*[value_to_filter_converter(value) for value in child_values])
        for builder in self.items_builder, self.count_builder:
            builder.data_source.add_join(
                builder.JoinType.INNER,
                data_source,
                "ON (%s.record_id = record.id)" % data_source
            )
            builder.main_filter &= child_entity_or_filter


    def create_external_object(self,
                               record_type,
                               record_id,
                               project_id,
                               project_alias,
                               root_group_id,
                               parent_category_id,
                               parent_category_datetime,
                               parent_category_finish_time,
                               level,
                               alias,
                               datetime,
                               comments,
                               finish_time,
                               base_directory,
                               name,
                               custom_parameters,
                               hashtag_info,
                               user_id=None
                               ):
        self._entity_provider.current_type = record_type
        if isinstance(custom_parameters, str):
            custom_parameters = json.loads(custom_parameters)
        project_emulator = ModelEmulator(
            id=project_id,
            alias=project_alias,
            root_group=None,
        )
        emulator = ModelEmulator(
            id=record_id,
            project=project_emulator,
            parent_category_id=parent_category_id,
            level=level,
            alias=alias,
            datetime=time_from_db(datetime),
            comments=comments,
            finish_time=time_from_db(finish_time),
            base_directory=base_directory,
            user=self._user_context,
            checked=user_id is not None,
            name=name,
            custom_parameters=custom_parameters,
        )

        if parent_category_id is None:
            emulator.add_field('parent_category', None)
        else:
            emulator.add_field('parent_category', ModelEmulator(
                id=parent_category_id,
                datetime=time_from_db(parent_category_datetime),
                finish_time=time_from_db(parent_category_finish_time),
                project=project_emulator
            ))

        if isinstance(hashtag_info, str):
            try:
                hashtag_info = json.loads(hashtag_info)
            except JSONDecodeError:
                hashtag_info = None
        if hashtag_info is not None and len(hashtag_info) > 0:
            hashtag_list = [
                ModelEmulator(
                    id=int(hashtag_id),
                    description=hashtag_description,
                    project=project_emulator,
                    type=LabjournalHashtagType.record,
                )
                for hashtag_id, hashtag_description in hashtag_info.items()
            ]
            emulator.add_field('hashtags', hashtag_list)

        return emulator
