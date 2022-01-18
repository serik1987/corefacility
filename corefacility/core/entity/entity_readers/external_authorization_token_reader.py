from .raw_sql_query_reader import RawSqlQueryReader
from .query_builders.query_filters import StringQueryFilter


class ExternalAuthorizationTokenReader(RawSqlQueryReader):
    """
    Reads information about the external authorization tokens from the database and sends them to the model providers
    """

    _query_debug = False
    """ Set this field to True to print token searching SQL queries for troubleshooting purposes. """

    def __init__(self, **kwargs):
        """
        Initializes the token reader

        :param kwargs: filters to apply. We support the only filter called 'authentication'
        """
        updated_kwargs = {}
        for name, value in kwargs.items():
            if name == "authentication":
                updated_kwargs["authentication_id"] = value.id
            else:
                updated_kwargs[name] = value
        super().__init__(**updated_kwargs)

    @property
    def lookup_table_name(self):
        """
        The main SQL table where information about all authorization tokens store.
        """
        if self._lookup_table_name is None:
            raise NotImplementedError("The _lookup_table_name is mandatory property for "
                                      "all authorization token readers")
        return self._lookup_table_name

    def initialize_query_builder(self):
        """
        Makes raw SQL request that corresponds to finding all authorization tokens in the entity.

        To retrieve additional information from the SQL table this method shall be overriden.
        """
        self.items_builder\
            .add_select_expression("%s.id" % self.lookup_table_name)\
            .add_select_expression("%s.authentication_id" % self.lookup_table_name)\
            .add_select_expression("core_authentication.user_id")\
            .add_data_source(self.lookup_table_name)
        self.items_builder.data_source\
            .add_join(self.items_builder.JoinType.INNER, "core_authentication",
                      "ON (core_authentication.id=%s.authentication_id)" % self.lookup_table_name)

        self.count_builder\
            .add_select_expression(self.count_builder.select_total_count())\
            .add_data_source(self.lookup_table_name)

    def apply_authentication_id_filter(self, auth):
        if type(auth) == int:
            auth_id = auth
        else:
            auth_id = auth.id
        self.items_builder.main_filter &= StringQueryFilter("authentication_id=%s", auth_id)

    def create_external_object(self, *args):
        """
        After successful execution of the SQL query the class will retrieve set of rows in the result table
        and call this method for each row (this is not true for executing len() function).

        The main purpose of this method is to transform a tuple of cells in the result table's row into the model
        emulator

        :param args: each argument is a value of a result table cell. The arguments follow in the same order
            as columns in the resultant table.
        :return: The core.entity.entity_readers.model_emulators.ModelEmulator instance
        """
        raise NotImplementedError("Please, implement the create_external_object method")
