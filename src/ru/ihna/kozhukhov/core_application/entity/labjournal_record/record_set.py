from enum import Enum

from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.entity.entity_sets.entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.models.enums.labjournal_record_type import LabjournalRecordType
from ru.ihna.kozhukhov.core_application.models import LabjournalRootRecord
from ru.ihna.kozhukhov.core_application.entity.readers.model_emulators import ModelEmulator
from .complex_interval import ComplexInterval
from .record_reader import RecordReader
from .root_record_provider import RootRecordProvider


class RecordSet(EntitySet):
    """
    Manipulates the list of labjournal records stored in the database

    Available filters:
    parent_category show children belonging to a particular parent_category (not suitable for the root record)
    user Defines the user context for the record (not suitable for the root record)
    alias The record alias (not suitable for the root record)
    type The record type filter (not suitable for the root record)
    """

    class LogicType(Enum):
        """
        Represents one of the predefined logic types
        """
        AND = "and"
        OR = "or"

    _entity_name = _("Laboratory journal record")
    """ Default human-readable name of the entity """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_record.record.Record"
    """ Base class of all entities containing inside this particular RecordSet """

    _entity_reader_class = RecordReader
    """ Entity readers are responsible for picking entities from the database """

    _root_record_provider = RootRecordProvider()
    """ Deals especially with root record """

    _entity_filter_list = {
        'parent_category':
            ("ru.ihna.kozhukhov.core_application.entity.labjournal_record.category_record.CategoryRecord", None),
        'user': ("ru.ihna.kozhukhov.core_application.entity.user.User", None),
        'alias': (str, None),
        'type': (LabjournalRecordType, None),
        'datetime': (ComplexInterval, None),
        'types': (list, None),
        'name': (str, None),
        'hashtags': (list, None),
        'hashtag_logic': (LogicType, None),
    }
    """ List of all entity filters """

    _alias_kwarg = None
    """
    The entity retrieval is available either by its numerical ID or by its full path which is not a database field
    """

    def get_root(self, project):
        """
        Reads the root record (the ordinary methods such as indexation, slicing, get(), len etc. usually doesn't
        read the parent categories)
        """
        try:
            external_object = LabjournalRootRecord.objects.get(project_id=project.id)
        except LabjournalRootRecord.DoesNotExist:
            external_object = ModelEmulator(
                comments=None,
                base_directory=None,
                project=project,
            )
        record = self._root_record_provider.wrap_entity(external_object)
        return record
