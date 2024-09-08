from ..readers.query_builders.data_source import SqlTable
from ..readers.model_emulators import ModelEmulator
from ..readers.query_builders.query_filters import StringQueryFilter
from ..readers.raw_sql_query_reader import RawSqlQueryReader
from ..labjournal_parameter_descriptor.parameter_descriptor_reader import ParameterDescriptorReader
from .viewed_parameter_provider import ViewedParameterProvider


class ViewedParameterReader(RawSqlQueryReader):
    """
    Reads the ViewedParameter objects from the database storage and puts them into the ViewedParameterSet
    container
    """

    _entity_provider = ViewedParameterProvider()
    """ Defines the provider that allows us to wrap the external object to the entity """

    _lookup_table_name = 'viewed_parameter'
    """ A table where entity IDs were stored """

    _query_debug = False
    """ Must be equal to False always except a special case of debugging this class """

    _category = None
    """ The category filter that was set """

    _user = None
    """ The user context that was set """

    def initialize_query_builder(self):
        """
        Constructs the default query builder
        """
        self.items_builder \
            .add_select_expression('viewed_parameter.id') \
            .add_select_expression(self.items_builder.quote_name('viewed_parameter.index')) \
            .add_select_expression('viewed_parameter.descriptor_id') \
            .add_select_expression('descriptor.type') \
            .add_select_expression(self.items_builder.quote_name('descriptor.index')) \
            .add_select_expression('descriptor.for_data_record') \
            .add_select_expression('descriptor.for_service_record') \
            .add_select_expression('descriptor.for_category_record') \
            .add_select_expression('descriptor.units') \
            .add_select_expression('descriptor.identifier') \
            .add_select_expression('descriptor.description') \
            .add_select_expression('descriptor.required') \
            .add_select_expression(self.items_builder.quote_name('descriptor.default')) \
            .add_data_source(SqlTable("core_application_labjournalparameterview", 'viewed_parameter')) \
            .add_order_term(self.items_builder.quote_name('viewed_parameter.index'))
        self.items_builder.data_source \
            .add_join(
                self.items_builder.JoinType.INNER,
                SqlTable('core_application_labjournalparameterdescriptor', 'descriptor'),
                "ON (descriptor.id = viewed_parameter.descriptor_id)"
            )

        self.count_builder \
            .add_select_expression(self.count_builder.select_total_count('viewed_parameter.id')) \
            .add_data_source(SqlTable("core_application_labjournalparameterview", 'viewed_parameter'))

    def apply_category_filter(self, category):
        """
        Applies the category filter to the viewed parameter list

        :param category: a category which filter must be applied
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("viewed_parameter.project_id=%s", category.project.id)
            if category.is_root_record:
                builder.main_filter &= StringQueryFilter("viewed_parameter.category_id IS NULL")
            else:
                builder.main_filter &= StringQueryFilter("viewed_parameter.category_id=%s", category.id)
        self._category = category

    def apply_user_filter(self, user):
        """
        Sets the user context for the viewed parameter list

        :param user: the user context to set
        """
        for builder in self.items_builder, self.count_builder:
            builder.main_filter &= StringQueryFilter("viewed_parameter.user_id=%s", user.id)
        self._user = user

    def create_external_object(self,
                               viewed_parameter_id,
                               index,
                               descriptor_id,
                               descriptor_type,
                               descriptor_index,
                               descriptor_for_data_record,
                               descriptor_for_service_record,
                               descriptor_for_category_record,
                               descriptor_units,
                               descriptor_identifier,
                               description,
                               required,
                               default,
                               ):
        """
        Constructs the external object

        :param viewed_parameter_id: ID of the viewed parameter
        :param index: index of the viewed parameter
        :param descriptor_id: descriptor of the viewed parameter to show
        :param descriptor_type: type of the parameter descriptor
        :param descriptor_index: index of descriptor
        :param descriptor_for_data_record: descriptor is for data record
        :param descriptor_for_service_record: descriptor is for service record
        :param descriptor_for_category_record: descriptor is for category record
        :param descriptor_units: measuring units for NumerParameterDescriptor and None for the other descriptors
        :param descriptor_identifier: idensitier of the descriptor
        :param description: custom parameter description
        :param required: True if the parameter is required to fill, False otherwise
        :param default: default value for the descriptor
        """
        if self._category is None:
            raise RuntimeError("The ViewedParameterReader can't work without the category filter")
        if self._user is None:
            raise RuntimeError("The ViewedParameterReader can't work without the user context set")
        descriptor_reader = ParameterDescriptorReader()
        descriptor_reader.apply_category_filter(self._category)
        return ModelEmulator(
            id=viewed_parameter_id,
            index=index,
            descriptor=descriptor_reader.create_external_object(
                descriptor_type,
                descriptor_id,
                descriptor_identifier,
                descriptor_index,
                description,
                required,
                default,
                descriptor_for_data_record,
                descriptor_for_service_record,
                descriptor_for_category_record,
                descriptor_units,
                None,
                None,
            ),
            category=self._category,
            user=self._user,
        )

    def __len__(self):
        """
        Selects total count
        """
        if self._category is None or self._user is None:
            raise RuntimeError("Either category or user context were not given")
        else:
            return super().__len__()
