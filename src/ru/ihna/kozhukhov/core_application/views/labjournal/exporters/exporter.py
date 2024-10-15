import os
import tempfile

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import CategoryRecord


class Exporter:
    """
    This is the base class for all machinery that exports the labjournal records to some external file
    """

    request = None
    """ An HTTP request processed by a given exporter """

    view = None
    """ A REST framework view that has created and called this exporter """

    export_file_extension = None
    """ An extension for the exported file (dot is included) """

    def __init__(self, request, view):
        """
        Initializes the exporter

        :param request: An HTTP request processed by a given exporter
        :param view: A REST framework view that has created and called this exporter
        """
        self.request = request
        self.view = view

    def create_new_frame(self, record_list: list, params: list):
        """
        Creates new file inside the temporary folder and writes all information about the records to that file.

        :param record_list: all information about the records. The argument value is a list where each item is a
            dictionary containing information about one particular labjournal record
        :param params: list of identifiers of all custom parameters to export
        :return: absolute path to the newly creating file. To get know about the absolute file name that should be
            you can call the create_temporary_file method - it creates a temporary file inside the temporary directory
        """
        raise NotImplementedError('create_new_frame')

    def extend_existent_frame(self, temporary_file: str, record_list: list, params: list):
        """
        Writes all information about records passed into this function at the end of an existent file inside the
        temporary folder and created by means of create_new_frame method

        :param temporary_file: The file which the labjournal records must be appended to
        :param params: list of identifiers of all custom parameters to export
        :param record_list: all information about the records. The argument value is a list where each item is a
            dictionary containing information about one particular labjournal record
        """
        raise NotImplementedError('extend_existent_frame')

    def create_temporary_file(self, close_file_after_create, text=True):
        """
        Creates new empty temporary file

        :param close_file_after_create: if True, the file will be immediately closed after create and name of the
        temporary file only will be returned. If False, the file will not be immediately closed after creation and
        the return result will be a tuple containing first a file object to newly created temporary file and second
        full absolute name of such a file.
        :param text: if close_file_after_create is False, specifies whether the file should be text or not
        :return: depends on value of the close_file_after_create (see above).
        """
        category_cue = self.request.parent_category.path[1:].replace('/', '_')
        if len(category_cue) > 0:
            category_cue += '.'
        file_prefix = "corefacility.{user}.{project}.{category}".format(
            user=self.request.user.login,
            project=self.request.project.alias,
            category=category_cue
        )
        temporary_file_descriptor, temporary_file_name = tempfile.mkstemp(
            suffix=self.export_file_extension,
            prefix=file_prefix,
            dir=tempfile.gettempdir(),
            text=text,
        )
        if close_file_after_create:
            os.close(temporary_file_descriptor)
            return temporary_file_name
        else:
            mode = 'w' if text else 'wb'
            return os.fdopen(temporary_file_descriptor, mode), temporary_file_name

    def get_custom_parameter(self, record, identifier):
        """
        Retrieves value of the custom parameter from a given record.
        If the custom parameter is not defined for a given record, default value of the custom parameter will be
        retrieved.

        :param record: a Labjournal record which custom parameter should be retrieved
        :param identifier: identifier of a custom parameter to retrieve
        :return: value of the custom parameter that shall be retrieved or None if such a custom parameter is not defined
        """
        if identifier in record.customparameters:
            value = record.customparameters[identifier]
        elif identifier in record.default_values:
            value = record.default_values[identifier]
        else:
            value = None
        return value
