from ru.ihna.kozhukhov.core_application.entity.readers.raw_sql_query_reader import RawSqlQueryReader
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import \
    StringQueryFilter, SearchQueryFilter

from .hashtag_provider import HashtagProvider


class HashtagReader(RawSqlQueryReader):
    """
    Reads information from the external storage and creates Hashtag objects based on such information
    """

    _query_debug = False
    """ Must be equal to False otherwise a special case of debugging this class """

    _entity_provider = HashtagProvider()
    """ The class is responsible for making Hashtag instances based on the database reading output """

    _project = None
    """ The project filter that is adjusted to a given hashtag """

    _type = None
    """ The type filter """

    def initialize_query_builder(self):
        """
        Plots the 'default' query that will be executed when no filters were applied
        """
        self.items_builder \
            .add_select_expression('id') \
            .add_select_expression('description') \
            .add_data_source('core_application_labjournalhashtag') \
            .add_order_term('description')

        self.count_builder \
            .add_select_expression(self.count_builder.select_total_count('id')) \
            .add_data_source('core_application_labjournalhashtag')

    def apply_project_filter(self, project):
        """
        Applies the project filter to a given reader

        :param project: the filter will pass only hashtags that belong to a given project
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("project_id=%s", project.id)
        self._project = project

    def apply_type_filter(self, hashtag_type):
        """
        Applies the type filter to a given hashtag

        :param hashtag_type: the filter will pass only hashtags of a given type
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("type=%s", str(hashtag_type))
        self._type = hashtag_type

    def apply_description_filter(self, description):
        """
        Filters only hashtags that start from a given description

        :param description: the description to start
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= SearchQueryFilter('description', description,
                                                     must_start=True)

    def create_external_object(self, hashtag_id, description):
        """
        Structures the output from the query execution

        :param hashtag_id: numerical ID of the hashtag that has been recently found
        :param description: Human-readable hashtag description
        """
        if self._project is None:
            raise RuntimeError("The HashtagSet requires the 'project' filter to be adjusted")
        if self._type is None:
            raise RuntimeError("The HashtagSet requires the 'type' filter to be adjusted")
        return ModelEmulator(
            id=hashtag_id,
            description=description,
            project=self._project,
            type=self._type
        )
