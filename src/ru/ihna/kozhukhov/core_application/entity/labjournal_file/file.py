import os

from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.fields import \
    RelatedEntityField, EntityField, ManagedEntityField, ReadOnlyField
from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import FileHashtagManager

from .file_set import FileSet
from .file_provider import FileProvider


class File(Entity):
    """
    The entity represents a connector between the corefacility model layer and the file itself
    """

    _entity_set_class = FileSet
    """ The class is used for make a container where all File objects are stored """

    _entity_provider_list = [FileProvider()]
    """ The file provider is responsible for information exchange between the File object and the database """

    _required_fields = ['record', 'name']
    """ The File instance can't be stored in the database until all these fields are filled """

    _public_field_description = {
        'record': RelatedEntityField("ru.ihna.kozhukhov.core_application.entity.labjournal_record.DataRecord",
                                     description="Experimental data record the file is attached to"),
        'name': EntityField(str, min_length=1, max_length=256,
                            description="File name (relatively to the base directory of the parent category"),
        'hashtags': ManagedEntityField(FileHashtagManager,
                                       description="Hashtags attached to a file"),
        'path': ReadOnlyField(description="Full path to a file"),
    }

    def __setattr__(self, name, value):
        """
        Assigns value to the entity field

        :param name: name of the field to assign
        :param value: new value of the field
        """
        super().__setattr__(name, value)
        if name == 'record' or name == 'name':
            self._update_path()

    def _update_path(self):
        """
        Updates the value of the 'path' field
        """
        if self._name is not None and self._record is not None \
                and self._record.parent_category.base_directory is not None:
            self._path = os.path.join(self._record.parent_category.base_directory, self._name)
        else:
            self._path = None
