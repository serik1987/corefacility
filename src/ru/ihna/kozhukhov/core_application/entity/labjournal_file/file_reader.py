import json

from ru.ihna.kozhukhov.core_application.entity.readers.raw_sql_query_reader import RawSqlQueryReader
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import StringQueryFilter
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.data_source import SqlTable
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator, time_from_db

from .file_provider import FileProvider
from ...models.enums import LabjournalHashtagType


class FileReader(RawSqlQueryReader):
    """
    Reads information about the record files from the database and stores it to the external storage
    """

    _query_debug = False
    """ Must be equal to False otherwise except of special case of testing this entity """

    _entity_provider = FileProvider()
    """ The provider that transforms the query output to the File object """

    _lookup_table_name = "file"
    """ Alias of a table where information about the file ID is contained """

    _record = None
    """
    When the record filter was adjusted, reflects the record value that has been set.
    Otherwise, the value of this property equals to None
    """

    def initialize_query_builder(self):
        """
        Adjusts the query builder for a special case where no entity set filters are set
        """
        self.items_builder \
            .add_select_expression("file.id") \
            .add_select_expression("file.name") \
            .add_select_expression("file.record_id") \
            .add_select_expression("record.project_id") \
            .add_select_expression("record.datetime") \
            .add_select_expression("record.parent_category_id") \
            .add_select_expression("parent_category.datetime") \
            .add_select_expression("parent_category.finish_time") \
            .add_select_expression("parent_category.base_directory") \
            .add_select_expression(self.items_builder.json_object_aggregation("hashtags.id", "hashtags.description")) \
            .add_data_source(SqlTable("core_application_labjournalfile", "file")) \
            .add_group_term('file.id')

        self.items_builder.data_source \
            .add_join(
                self.items_builder.JoinType.INNER,
                SqlTable("core_application_labjournalrecord", "record"),
                "ON (record.id = file.record_id)"
            ) \
            .add_join(
                self.items_builder.JoinType.LEFT,
                SqlTable("core_application_labjournalrecord", "parent_category"),
                "ON (parent_category.id = record.parent_category_id)"
            ) \
            .add_join(
                self.items_builder.JoinType.LEFT,
                SqlTable("core_application_labjournalfilehashtag", "hashtag_associations"),
                "ON (hashtag_associations.file_id = file.id)"
            ) \
            .add_join(
                self.items_builder.JoinType.LEFT,
                SqlTable("core_application_labjournalhashtag", "hashtags"),
                "ON (hashtags.id = hashtag_associations.hashtag_id)"
            )

        self.count_builder \
            .add_select_expression(self.count_builder.select_total_count("file.id")) \
            .add_data_source(SqlTable("core_application_labjournalfile", "file"))

    def apply_record_filter(self, record):
        """
        Filters only such files that are attached to a given record

        :param record: the experimental data record to be used for a filter
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("file.record_id=%s", record.id)
        self._record = record

    def create_external_object(self,
                               file_id,
                               file_name,
                               record_id,
                               project_id,
                               record_datetime,
                               parent_category_id,
                               parent_category_datetime,
                               parent_category_finish_time,
                               base_directory,
                               hashtag_info,
                               ):
        """
        Transforms the query execution output to the model emulator what will be further transformed to the File
        object by the FileProvider

        :param file_id: numerical ID of the file
        :param file_name: name of the file
        :param record_id: numerical ID of a record which the file is attached to
        :param project_id: project from which the file is accessible
        :param record_datetime: date and time of a record the file is attached to
        :param parent_category_id: ID of a parent category to load
        :param parent_category_datetime: date and time of the parent category
        :param parent_category_finish_time: finish time of the parent category
        :param base_directory: the base directory of a parent category of a record the file is attached to
        :param hashtag_info: information about all hashtags revealed by means of the JSON aggregation function
        """
        if self._record is None:
            project_emulator = ModelEmulator(
                id=project_id
            )
            record_external_object = ModelEmulator(
                id=record_id,
                parent_category_id=parent_category_id,
                datetime=time_from_db(record_datetime),
                project=project_emulator,
            )
            if parent_category_id is None:
                record_external_object.add_field('parent_category', None)
            else:
                record_external_object.add_field('parent_category', ModelEmulator(
                    id=parent_category_id,
                    datetime=time_from_db(parent_category_datetime),
                    finish_time=time_from_db(parent_category_finish_time),
                ))
        else:
            record_external_object = self._record
            project_emulator = self._record.project

        external_object = ModelEmulator(
            id=file_id,
            name=file_name,
            record=record_external_object
        )

        if isinstance(hashtag_info, str):
            try:
                hashtag_info = json.loads(hashtag_info)
            except json.JSONDecodeError:
                hashtag_info = None
        if hashtag_info is not None:
            hashtag_list = [
                ModelEmulator(
                    id=int(hashtag_id),
                    description=hashtag_description,
                    project=project_emulator,
                    type=LabjournalHashtagType.file,
                )
                for hashtag_id, hashtag_description in hashtag_info.items()
            ]
            external_object.add_field('hashtags', hashtag_list)

        return external_object
