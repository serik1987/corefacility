from ru.ihna.kozhukhov.core_application.entity.labjournal_file import File
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from .entity_set_object import EntitySetObject


class LabjournalFileSetObject(EntitySetObject):
    """
    A temporary container where different instances of the labjournal's File are stored for testing purpose
    """

    _entity_class = File
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    record_set_object = None
    """ The record set object that is used for child entities """

    sample_files = ["neurons.dat", "imaging.dat", "behavior.avi"]
    """ These three files will be attached to each record """

    def __init__(self, record_set_object, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param record_set_object: set of record entities, just for child data records
        :param _entity_list: This is an internal argument. Don't use it.
        """
        self.record_set_object = record_set_object
        super().__init__(_entity_list=_entity_list)

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        data_records = list(filter(
            lambda record: record.type == LabjournalRecordType.data, self.record_set_object.entities
        ))
        file_data = [
            {
                'record': record,
                'name': filename
            }
            for filename in self.sample_files
            for record in data_records
        ]
        return file_data

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self.record_set_object, _entity_list=list(self._entities))

    def sort(self):
        """
        Sorts all entities inside the container in ascending mode
        """
        self._entities = sorted(self._entities, key=lambda labjournal_file: labjournal_file.id)

    def filter_by_record(self, record):
        """
        Filters only those files that are attached to a given experimental data record
        """
        self._entities = list(filter(lambda labjournal_file: labjournal_file.record.id == record.id, self._entities))
