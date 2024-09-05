from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.boolean_parameter_descriptor import \
    BooleanParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.number_parameter_descriptor import \
    NumberParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.string_parameter_descriptor import \
    StringParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.discrete_parameter_descriptor import \
    DiscreteParameterDescriptor
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from .entity_set_object import EntitySetObject


class ParameterDescriptorSetObject(EntitySetObject):
    """
    Creates environment for testing the parameter descriptors
    """

    _record_set_object = None
    """ The test environment for the parent objects (the labjournal records) """

    _entity_class = BooleanParameterDescriptor
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    def __init__(self, record_set_object, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param _entity_list: This is an internal argument. Don't use it.
        """
        self._record_set_object = record_set_object
        if _entity_list is not None:
            super().__init__(_entity_list=_entity_list)
        else:
            self._entities = list()
            for project in self._record_set_object.optical_imaging, self._record_set_object.the_rabbit_project:
                root_record = RootCategoryRecord(project=project)
                self._add_descriptors_for_category(root_record)
                root_children = root_record.children
                for category_alias in 'a', 'b':
                    root_children.alias = category_alias
                    category = root_children[0]
                    self._add_descriptors_for_category(category)
                    if category_alias == 'a':
                        subcategory = category.children[0]
                        self._add_descriptors_for_category(subcategory)

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._record_set_object, _entity_list=list(self._entities))

    def filter_by_category(self, category):
        """
        Remains only those records that have a certain category

        :param category: a category to filter
        """
        self._entities = list(filter(
            lambda descriptor: descriptor.category.id == category.id and \
                               descriptor.category.project.id == category.project.id,
            self._entities
        ))

    def _add_descriptors_for_category(self, category):
        """
        Adds descriptors for a given category

        :param category: a category for which descriptors must be added
        """
        if category.is_root_record:
            alias_prefix = "root"
        else:
            alias_prefix = category.alias

        boolean_descriptor = BooleanParameterDescriptor(
            category=category,
            identifier=alias_prefix + "_bool",
            description="Тестовый булев дескриптор",
            required=False,
            record_type=[LabjournalRecordType.data,],
        )
        boolean_descriptor.create()
        self._entities.append(boolean_descriptor)

        number_descriptor = NumberParameterDescriptor(
            category=category,
            identifier=alias_prefix + "_num",
            description="Тестовый числовой дескриптор",
            required=True,
            record_type=[LabjournalRecordType.service,],
            units="единиц",
        )
        number_descriptor.create()
        self._entities.append(number_descriptor)

        string_descriptor = StringParameterDescriptor(
            category=category,
            identifier=alias_prefix + "_string",
            description="Тестовый строковой дескриптор",
            required=False,
            record_type=[LabjournalRecordType.category,],
        )
        string_descriptor.create()
        self._entities.append(string_descriptor)

        discrete_value_descriptor = DiscreteParameterDescriptor(
            category=category,
            identifier=alias_prefix + "_discrete",
            description="Дескриптор дискретного параметра",
            required=True,
            record_type=[LabjournalRecordType.data, LabjournalRecordType.service,],
        )
        discrete_value_descriptor.create()
        self._entities.append(discrete_value_descriptor)
