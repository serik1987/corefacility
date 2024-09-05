from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor.boolean_parameter_descriptor import \
    BooleanParameterDescriptor
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.root_category_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType

from .entity_object import EntityObject
from ..labjournal_test_mixin import LabjournalTestMixin


class ParameterDescriptorObject(LabjournalTestMixin, EntityObject):
    """
    This is an auxiliary object to test the parameter descriptors
    """

    _entity_class = BooleanParameterDescriptor
    """ The entity class that is used to create the entity itself """

    _default_create_kwargs = {
        'category': None,
        'identifier': 'id',
        'description': "Описание сущности",
        'required': False,
        'record_type': [LabjournalRecordType.data]
    }
    """ The default field values that will be assigned to the entity if nothing else will be given to the user """

    _default_change_kwargs = {
        'identifier': 'id2',
        'description': "Другое описание сущности",
        'required': True,
        'record_type': [LabjournalRecordType.data, LabjournalRecordType.service],
    }
    """ The default field values that shall be changed by the entity if nothing else will be given to the user """

    category = None
    """ A category which descriptors are considered """


    def __init__(self, use_defaults=True, **kwargs):
        """
        Checks the entity to test and puts it inside the entity object

        :param use_defaults: if True, the constructor will use the _default_create_kwargs fields. Otherwise, this
        class property will be ignored
        :param kwargs: Any additional field values that shall be assigned to the entity or 'id' that reflects the
        entity ID
        """
        self.category = \
            self._default_create_kwargs['category'] = RootCategoryRecord(project=self.optical_imaging).children[0]
        super().__init__(use_defaults=use_defaults, **kwargs)

    def reload_entity(self):
        """
        Loads the recently saved entity from the database

        :return: nothing
        """
        if self._id is None:
            raise RuntimeError("EntityObject.reload_entity: can't reload the entity that is recently saved")
        entity_set = self.category.descriptors
        self._entity = entity_set.get(self._id)
