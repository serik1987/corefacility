import hashlib

from django.core.files import File
from django.db import transaction
from django.conf import settings

from ...entity.field_managers.entity_value_manager import EntityValueManager
from ...exceptions.entity_exceptions import EntityOperationNotPermitted


class PublicFileManager(EntityValueManager):
    """
    Manager attaching and detaching of public file.

    We call 'public files' such files that are:
    (a) attached to a certain field of the entity
    (b) can be uploaded by everybody who has entity access
    (c) can be downloaded by everybody including non-authorized users
    (d) doesn't require the corefacility application to be downloaded (i.e., they will be downloaded faster).
    """

    _include_media_root = None

    @staticmethod
    def compute_hash(filename):
        """
        Computes the file hash. The file hash is unique for each file content.
        :param filename: filename to open
        :return: file hash
        """
        full_name = settings.MEDIA_ROOT + "/" + filename
        hash_md5 = hashlib.md5()
        with open(full_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def __init__(self, value, default_value=None, include_media_root: bool = True):
        """
        Initializes the public file manager
        :param value: Internal value of the field (must be an instance of django.core.files.File class)
        :param default_value: value of the property when value doesn't refer to any file
        :param include_media_root: True to include media URL to the file URL, False otherwise
        """
        super().__init__(value, default_value)
        self._include_media_root = include_media_root

    def attach_file(self, file: File) -> None:
        """
        Attaches external file to tje entity
        No any additional save/retrieve is needed but the entity state must be either 'loaded' or 'saved'.
        The function does not validate or process the file: this is a view responsibility to do this
        :param file: an instance of django.core.files.File object containing the attached file
        :return: nothing
        """
        if self.entity.state != "loaded" and self.entity.state != "saved":
            raise EntityOperationNotPermitted()
        self.entity.check_entity_providers_defined()
        with transaction.atomic():
            self.detach_file()
            for provider in self.entity._entity_provider_list:
                provider.attach_file(self.entity, self.field_name, file)
            self._field_value = getattr(self.entity, '_' + self.field_name)

    def detach_file(self) -> None:
        """
        Detaches external file from the entity.
        No any additional save/retrieve is needed but the entity state must be either 'loaded' or 'saved'.

        :return: nothing
        """
        if self.is_detached:
            return
        if self.entity.state != "loaded" and self.entity.state != "saved":
            raise EntityOperationNotPermitted()
        self.entity.check_entity_providers_defined()
        with transaction.atomic():
            for provider in self.entity._entity_provider_list:
                provider.detach_file(self.entity, self.field_name)
            self._field_value = None

    @property
    def is_detached(self):
        """
        Checks whether some file attached to this field

        :return: True is not files attached to this field
        """
        return self._field_value is None or self._field_value.name is None or self._field_value.name == ""

    @property
    def url(self) -> str:
        """
        Returns the file URL
        """
        if self.is_detached:
            filename = self._default_value
        else:
            filename = self._field_value.name
            if self._include_media_root:
                try:
                    sign = self.compute_hash(filename)
                    filename = settings.MEDIA_URL + filename + "?{hash}".format(hash=sign)
                # We need to add file hashing to clear browser cache in the following way:
                # /static/core/user_avatar.jpg?hash1 and /static/code/user_avatar.jpg?hash2
                # were treated as same files by the Server but different ones by the Web browser.
                # If the Web browser saved /static/core/user_avatar.jpg?hash1 in cache, it will not
                # retrieve the cache to obtain /static/code/user_avatar.jpg?hash2
                except FileNotFoundError:
                    filename = self._default_value
                     # If someone deletes the file, we will return the default value. The user
                     # can upload the file again!
        return filename

    def __eq__(self, other):
        """
        Two file fields are equal if and only if their URLs are equal

        :param other: the other file field
        :return: True if two files are equal
        """
        return self.url == other.url
