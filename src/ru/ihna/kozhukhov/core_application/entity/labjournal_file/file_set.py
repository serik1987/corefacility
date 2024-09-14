from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.entity.entity_sets.entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import DataRecord

from .file_reader import FileReader


class FileSet(EntitySet):
    """
    Represents a container where different labjournal files are stored
    """

    _entity_name = _("File attached to the experimental data record")
    """ Human-readable entity name """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_file.File"
    """ Class of all entities contained in this container """

    _entity_reader_class = FileReader
    """
    The file reader reads information about the file from the external storage and makes File instances based on
    such information
    """

    _entity_filter_list = {
        'record': (DataRecord, lambda record: record.state != 'creating' and record.state != 'deleted'),
    }
