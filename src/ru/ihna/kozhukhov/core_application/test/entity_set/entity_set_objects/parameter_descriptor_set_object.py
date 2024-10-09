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

    _alias_field = 'identifier'
    """ Need to search by alias """

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

    def set_custom_parameters(self):
        """
        Sets custom parameters for certain set of records

        :return: a dictionary contains all categories which child records properly set their custom parameters
        """
        parent_categories = dict()

        for record in self._record_set_object.entities:
            if record.level == 1 and record.alias == 'a':
                parent_categories['a'] = record
            elif record.level == 1 and record.alias == 'b':
                parent_categories['b'] = record
            elif record.level == 2 and record.parent_category.alias == 'a':
                if hasattr(record, 'alias') and record.alias == 'a1':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'grat'
                    record.custom_a_bool = False
                    record.custom_a_num = 1
                    record.custom_a_string = "Вася"
                    record.custom_a_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a2':
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a3':
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'imag'
                    record.custom_a_string = "Коля"
                    record.custom_a_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a4':
                    record.custom_root_bool = True
                    record.custom_root_num = 1
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'squares'
                    record.custom_a_bool = True
                    record.custom_a_num = 2
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a5':
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'triang'
                    record.custom_a_string = "Петя"
                    record.custom_a_discrete = 'imag'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a6':
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'a7':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'ret'
                    record.custom_a_bool = False
                    record.custom_a_num = 3
                    record.custom_a_string = "Игорь"
                    record.custom_a_discrete = 'squares'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 1":
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'imag'
                    record.custom_a_num = 1
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 2":
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'squares'
                    record.custom_a_string = "Вася"
                    record.custom_a_discrete = 'triang'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 3":
                    record.custom_root_bool = True
                    record.custom_root_num = 1
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'triang'
                    record.custom_a_bool = True
                    record.custom_a_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 4":
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'grat'
                    record.custom_a_num = 2
                    record.custom_a_string = "Коля"
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 5":
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'subcat':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'imag'
                    record.custom_a_bool = False
                    record.custom_a_string = "Петя"
                    record.update()
            elif record.level == 2 and record.parent_category.alias == 'b':
                if hasattr(record, 'alias') and record.alias == 'b1':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'grat'
                    record.custom_b_bool = False
                    record.custom_b_num = 1
                    record.custom_b_string = "Вася"
                    record.custom_b_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b2':
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b3':
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'imag'
                    record.custom_b_string = "Коля"
                    record.custom_b_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b4':
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'squares'
                    record.custom_b_bool = True
                    record.custom_b_num = 2
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b5':
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'triang'
                    record.custom_b_string = "Петя"
                    record.custom_b_discrete = 'imag'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b6':
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'b7':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'ret'
                    record.custom_b_bool = False
                    record.custom_b_num = 3
                    record.custom_b_string = "Игорь"
                    record.custom_b_discrete = 'squares'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 1":
                    record.custom_root_bool = True
                    record.custom_root_num = 2
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'imag'
                    record.custom_b_num = 1
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 2":
                    record.custom_root_bool = False
                    record.custom_root_num = 3
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'squares'
                    record.custom_b_string = "Вася"
                    record.custom_b_discrete = 'triang'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 3":
                    record.custom_root_bool = True
                    record.custom_root_num = 1
                    record.custom_root_string = "Коля"
                    record.custom_root_discrete = 'triang'
                    record.custom_b_bool = True
                    record.custom_b_discrete = 'grat'
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 4":
                    record.custom_root_bool = False
                    record.custom_root_num = 2
                    record.custom_root_string = "Петя"
                    record.custom_root_discrete = 'grat'
                    record.custom_b_num = 2
                    record.custom_b_string = "Коля"
                    record.update()
                elif hasattr(record, 'name') and record.name == "Служебная запись 5":
                    record.custom_root_bool = True
                    record.custom_root_num = 3
                    record.custom_root_string = "Игорь"
                    record.custom_root_discrete = 'ret'
                    record.update()
                elif hasattr(record, 'alias') and record.alias == 'subcat':
                    record.custom_root_bool = False
                    record.custom_root_num = 1
                    record.custom_root_string = "Вася"
                    record.custom_root_discrete = 'imag'
                    record.custom_b_bool = False
                    record.custom_b_string = "Петя"
                    record.update()

        return parent_categories
