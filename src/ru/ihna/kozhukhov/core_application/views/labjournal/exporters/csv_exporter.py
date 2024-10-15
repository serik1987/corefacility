import csv

from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType

from .exporter import Exporter


class CsvExporter(Exporter):
    """
    Implements the data export to CSV format
    """

    MINUTE = 60
    """ Number of seconds per one minute """

    export_file_extension = ".csv"
    """ An extension for the exported file (dot is included) """

    csv_file_kwargs = {}
    """
    Additional keyword arguments to be passed to csv.writer function.
    They define detailed options of the export file format.
    """

    COLUMN_NAMES = [
        'path',
        'level',
        'type',
        'alias',
        'name',
        'absolute_datetime',
        'relative_datetime_min',
        'finish_datetime',
        'comments',
    ]
    """ Names of columns inside the csv file """

    def create_new_frame(self, record_list: list, params: list):
        """
        Creates new file inside the temporary folder and writes all information about the records to that file.

        :param record_list: all information about the records. The argument value is a list where each item is a
            dictionary containing information about one particular labjournal record
        :param params: list of identifiers of all custom parameters to export
        :return: absolute path to the newly creating file. To get know about the absolute file name that should be
            you can call the create_temporary_file method - it creates a temporary file inside the temporary directory
        """
        temporary_file, temporary_file_name = self.create_temporary_file(False)
        try:
            writer = csv.writer(temporary_file, **self.csv_file_kwargs)
            writer.writerow(self.COLUMN_NAMES + params)
            self.write_data(writer, record_list, params)
        finally:
            temporary_file.close()
        return temporary_file_name

    def extend_existent_frame(self, temporary_file: str, record_list: list, params: list):
        """
        Writes all information about records passed into this function at the end of an existent file inside the
        temporary folder and created by means of create_new_frame method

        :param temporary_file: The file which the labjournal records must be appended to
        :param params: list of identifiers of all custom parameters to export
        :param record_list: all information about the records. The argument value is a list where each item is a
            dictionary containing information about one particular labjournal record
        """
        with open(temporary_file, 'a') as temporary_file_handler:
            writer = csv.writer(temporary_file_handler, **self.csv_file_kwargs)
            self.write_data(writer, record_list, params)

    def write_data(self, writer, record_list, params):
        """
        Appends the data to existent CSV file

        :param writer: a CSV writer that related to such a file
        :param record_list: list of labjournal records to export
        :param params: list of custom parameters that are required to be exported
        """
        for record in record_list:
            file_row = [
                record.path if record.type != LabjournalRecordType.service else 'service-%d' % record.id,
                record.level,
                record.type.name,
                record.alias if record.type != LabjournalRecordType.service else None,
                record.name if record.type == LabjournalRecordType.service else None,
                record.datetime.strftime("%Y-%m-%dT%H-%M-%S") if record.datetime is not None else None,
                record.relative_time.total_seconds() / self.MINUTE if record.relative_time is not None else None,
                record.finish_time.strftime("%Y-%m-%dT%H-%M-%S")
                    if record.type == LabjournalRecordType.category and record.finish_time is not None else None,
                record.comments,
            ] + [
                self.get_custom_parameter(record, param) for param in params
            ]
            writer.writerow(file_row)
