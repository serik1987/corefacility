from django.core.files import File
from .entity_value_manager import EntityValueManager


class PublicFileManager(EntityValueManager):
    """
    Manager attaching and detaching of public file.

    We call 'public files' such files that are:
    (a) attached to a certain field of the entity
    (b) can be uploaded by everybody who has entity access
    (c) can be downloaded by everybody including non-authorized users
    (d) doesn't require the corefacility application to be downloaded (i.e., they will be downloaded faster).
    """

    def attach_file(self, file: File) -> None:
        """
        Attaches external file to tje entity.
        The function does not validate or process the file: this is a view responsibility to do this

        :param file: an instance of django.core.files.File object containing the attached file
        :return: nothing
        """
        raise NotImplementedError("TO-DO: attach file to the entity")

    def detach_file(self) -> None:
        """
        Detaches external file from the entity

        :return: nothing
        """
        raise NotImplementedError("TO-DO: detach file from the entity")

    @property
    def url(self) -> str:
        """
        Returns the file URL
        """
        if self._field_value is None or self._field_value.name is None or self._field_value.name == "":
            return self._default_value
        else:
            raise NotImplementedError("TO-DO: url property")

    def __eq__(self, other):
        """
        Two file fields are equal if and only if their URLs are equal

        :param other: the other file field
        :return: True if two files are equal
        """
        return self.url == other.url
