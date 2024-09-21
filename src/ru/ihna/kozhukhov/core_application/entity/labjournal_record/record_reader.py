from datetime import timedelta
import json
from json import JSONDecodeError
from django.conf import settings

from ru.ihna.kozhukhov.core_application.entity.readers.raw_sql_query_reader import RawSqlQueryReader
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator, time_from_db, prepare_time
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.data_source import SqlTable, Subquery
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import \
    StringQueryFilter, OrQueryFilter, SearchQueryFilter, AndQueryFilter
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType, LabjournalRecordType

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
        if self._hashtag_logic_filter is not None:
            if len(hashtags) > 0:
                if self._hashtag_logic_filter.value == "and":
                    self.apply_hashtags_and_filter(hashtags)
                elif self._hashtag_logic_filter.value == "or":
                    self.apply_hashtags_or_filter(hashtags)
            else:
                self._hashtag_filter = hashtags

    def apply_hashtag_logic_filter(self, hashtag_logic):
        """
        Defines the logic that the hashtags should be applied

        :param hashtag_logic: one out of the predefined hashtag logic
        """
        if self._hashtag_filter is not None:
            if len(self._hashtag_filter) > 0:
                if hashtag_logic.value == "and":
                    self.apply_hashtags_and_filter(self._hashtag_filter)
                elif hashtag_logic.value == "or":
                    self.apply_hashtags_or_filter(self._hashtag_filter)
        else:
            self._hashtag_logic_filter = hashtag_logic

    def apply_hashtags_and_filter(self, hashtags):
        """
        Passes only records that contains all given hashtags

        :param hashtags: list of hashtag entities or IDs
        """
        hashtags = [hashtag.id if isinstance(hashtag, RecordHashtag) else hashtag for hashtag in hashtags]
        subquery_builder = settings.QUERY_BUILDER_CLASS()
        subquery_builder \
            .add_select_expression("record_id") \
            .add_select_expression(subquery_builder.select_total_count('hashtag_id'), alias="hashtag_count") \
            .add_data_source("core_application_labjournalhashtagrecord") \
            .set_main_filter(OrQueryFilter(*[
                StringQueryFilter("hashtag_id=%s", hashtag_id) for hashtag_id in hashtags
            ])) \
            .add_group_term("record_id")

        for builder in self.items_builder, self.count_builder:
            builder.data_source.add_join(
                self.items_builder.JoinType.INNER,
                Subquery(subquery_builder, "hashtag_stats"),
                "ON (hashtag_stats.record_id = record.id)"
            )
            builder.main_filter &= StringQueryFilter("hashtag_stats.hashtag_count=%s", len(hashtags))

    def apply_hashtags_or_filter(self, hashtags):
        """
        Passes only records that contain any of the given hashtag

        :param hashtags: list of hashtag entities of  IDs
        """
        hashtags = [hashtag.id if isinstance(hashtag, RecordHashtag) else hashtag for hashtag in hashtags]
        filter_condition = OrQueryFilter(*[
            StringQueryFilter("hashtag_filter.hashtag_id=%s", hashtag_id) for hashtag_id in hashtags
        ])
        for builder in self.items_builder, self.count_builder:
            builder.data_source.add_join(
                self.items_builder.JoinType.INNER,
                SqlTable("core_application_labjournalhashtagrecord", "hashtag_filter"),
                "ON (hashtag_filter.record_id = record.id)"
            )
            builder.main_filter &= filter_condition


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
