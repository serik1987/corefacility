import json

from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.data_source import SqlTable
from ru.ihna.kozhukhov.core_application.entity.readers.raw_sql_query_reader import RawSqlQueryReader
from ru.ihna.kozhukhov.core_application.entity.readers.query_builders.query_filters import StringQueryFilter
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType, LabjournalRecordType

from .parameter_descriptor_provider import ParameterDescriptorProvider


class ParameterDescriptorReader(RawSqlQueryReader):
    """
    Reads information about parameter descriptors from the database and forms the ParameterDescriptor instances
    """

    _query_debug = False
    """ Should be equal to False everywhere except a special case of debugging this class """

    _entity_provider = ParameterDescriptorProvider()
    """
    The instance of the entity provider. When the EntityReader finds an information about
    the entity from the external source that satisfies filter conditions, it calls the
    wrap_entity method of the _entity_provider given here
    """

    _category = None
    """A reader where no category was selected is unsuitable
    """

    _lookup_table_name = "descriptor"
    """ A table which IDs are uniquely relate to the whole entities """

    def initialize_query_builder(self):
        """
        This function shall call certain methods for the query builder to make
        it to generate proper queries given that no external filters applied

        :return: nothing
        """
        self.items_builder \
            .add_select_expression('descriptor.type') \
            .add_select_expression('descriptor.id') \
            .add_select_expression('descriptor.identifier') \
            .add_select_expression(self.items_builder.quote_name('descriptor.index')) \
            .add_select_expression('descriptor.description') \
            .add_select_expression('descriptor.required') \
            .add_select_expression(self.items_builder.quote_name('descriptor.default')) \
            .add_select_expression('descriptor.for_data_record') \
            .add_select_expression('descriptor.for_service_record') \
            .add_select_expression('descriptor.for_category_record') \
            .add_select_expression('descriptor.units') \
            .add_select_expression(
                self.items_builder.json_object_aggregation('available_values.id', 'available_values.alias')
            ) \
            .add_select_expression(
                self.items_builder.json_object_aggregation('available_values.id', 'available_values.description')
            ) \
            .add_select_expression(
                self.items_builder.json_object_aggregation('hashtag.id', 'hashtag.description')
            ) \
            .add_data_source(SqlTable('core_application_labjournalparameterdescriptor', 'descriptor')) \
            .add_group_term("descriptor.id") \
            .add_order_term(
                self.items_builder.quote_name('descriptor.index'),
                self.items_builder.ASC,
                self.items_builder.NULLS_LAST,
            ) \
            .add_order_term('descriptor.id', self.items_builder.ASC)
        self.count_builder \
            .add_data_source(SqlTable('core_application_labjournalparameterdescriptor', 'descriptor')) \
            .add_select_expression(self.count_builder.select_total_count('descriptor.id'))

        self.items_builder.data_source \
            .add_join(
                self.items_builder.JoinType.LEFT,
                SqlTable("core_application_labjournalparameteravailablevalue", "available_values"),
                "ON (available_values.descriptor_id = descriptor.id)"
            ) \
            .add_join(
                self.items_builder.JoinType.LEFT,
                SqlTable("core_application_labjournaldescriptorhashtag", "hashtag_connection"),
                "ON (hashtag_connection.descriptor_id = descriptor.id)"
            ) \
            .add_join(
                self.items_builder.JoinType.LEFT,
                SqlTable("core_application_labjournalhashtag", "hashtag"),
                "ON (hashtag.id = hashtag_connection.hashtag_id)"
            )

    def apply_category_filter(self, category):
        """
        Filters only those descriptors that have certain category

        :param category: a category to apply
        """
        if category is None:
            raise ValueError("Value of the category filter must be a valid category")
        for builder in self.items_builder, self.count_builder:
            if category.id is None:
                builder.main_filter &= StringQueryFilter("descriptor.category_id IS NULL")
            else:
                builder.main_filter &= StringQueryFilter("descriptor.category_id=%s", category.id)
            builder.main_filter &= StringQueryFilter("descriptor.project_id=%s", category.project.id)
        self._category = category

    def create_external_object(self,
                               descriptor_type,
                               descriptor_id,
                               identifier,
                               index,
                               description,
                               required,
                               default,
                               for_data_record,
                               for_service_record,
                               for_category_record,
                               units,
                               available_values_alias,
                               available_values_description,
                               hashtag_info,
                               ):
        """
        Transforms the query result row into any external object that is able to read by the entity reader
        """
        record_types = list()

        if default is not None:
            if descriptor_type == 'B':  # BooleanParameterDescriptor
                default = default == 'True'
            elif descriptor_type == 'N':  # NumberParameterDescriptor
                default = float(default)

        if for_data_record:
            record_types.append(LabjournalRecordType.data)
        if for_service_record:
            record_types.append(LabjournalRecordType.service)
        if for_category_record:
            record_types.append(LabjournalRecordType.category)
        if self._category is None:
            raise RuntimeError("The reader can't work when no category was selected")

        external_object = ModelEmulator(
            type=descriptor_type,
            id=descriptor_id,
            category=self._category,
            identifier=identifier,
            index=index,
            description=description,
            required=required,
            default=default,
            record_type=record_types,
        )

        if descriptor_type == 'N':
            external_object.units = units

        if descriptor_type == 'D' and available_values_alias is not None and available_values_description is not None \
                and available_values_alias != "{:null}" and available_values_description != "{:null}":
            if isinstance(available_values_alias, str):
                available_values_alias = json.loads(available_values_alias)
            if isinstance(available_values_description, str):
                available_values_description = json.loads(available_values_description)
            available_values = list()
            for value_id_str in available_values_alias.keys():
                value_id = int(value_id_str)
                value_alias = available_values_alias[value_id_str]
                value_description = available_values_description[value_id_str]
                available_values.append({
                    'id': value_id,
                    'alias': value_alias,
                    'description': value_description,
                })
            external_object.add_field('values', available_values)

        if isinstance(hashtag_info, str):
            try:
                hashtag_info = json.loads(hashtag_info)
            except json.JSONDecodeError:
                hashtag_info = None
        if hashtag_info is not None:
            hashtag_list = list()
            for hashtag_id, hashtag_description in hashtag_info.items():
                hashtag_list.append(ModelEmulator(
                    id=int(hashtag_id),
                    description=hashtag_description,
                    project=self._category.project,
                    type=LabjournalHashtagType.record,
                ))
            external_object.add_field('hashtags', hashtag_list)

        return external_object
