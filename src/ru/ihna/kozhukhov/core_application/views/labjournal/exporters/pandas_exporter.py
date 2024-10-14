from dateutil.parser import parse
import pandas
from rest_framework.exceptions import ValidationError

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import CategoryRecord
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from .exporter import Exporter


class PandasExporter(Exporter):
    """
    Provides the data export to the Pandas DataFrame format
    """

    MINUTE = 60
    """ Number of seconds per a single minute """

    export_file_extension = ".json"
    """ An extension for the exported file (dot is included) """

    def create_new_frame(self, record_list: list, params: list):
        """
        Creates new file inside the temporary folder and writes all information about the records to that file.

        :param record_list: all information about the records. The argument value is a list where each item is a
            dictionary containing information about one particular labjournal record
        :param params: list of identifiers of all custom parameters to export
        :return: absolute path to the newly creating file. To get know about the absolute file name that should be
            you can call the make_temporary_file method - it creates a temporary file inside the temporary directory
        """
        record_frame = self._convert_records_to_frame(record_list, params)
        record_file = self.create_temporary_file(True)
        record_frame.to_json(record_file)
        return record_file

    def extend_existent_frame(self, temporary_file: str, record_list: list, params: list):
        """
        Writes all information about records passed into this function at the end of an existent file inside the
        temporary folder and created by means of create_new_frame method

        :param temporary_file: The file which the labjournal records must be appended to
        :param params: list of identifiers of all custom parameters to export
        :param record_list: all information about the records. The argument value is a list where each item is a
            dictionary containing information about one particular labjournal record
        """
        try:
            existent_frame = pandas.read_json(temporary_file)
        except ValueError:
            raise ValidationError({'tmp_file': "The temporary file doesn't have a PANDAS json format"})
        appending_frame = self._convert_records_to_frame(record_list, params)
        try:
            result_frame = pandas.concat((existent_frame, appending_frame))
            result_frame.to_json(temporary_file)
        except ValueError:
            raise ValidationError("Data chunks inconsistency. Probably, you have already followed this link")

    def _convert_records_to_frame(self, record_list: list, params: list):
        """
        Converts records in the record list to one single pandas DataFrame that relates to data chunk inside the
        exported file

        :param record_list: information about labjournal records to convert. The argument value is a list where each
            item is a dictionary containing information about one particular labjournal record
        :param params: list of identifiers of all custom parameters to export
        :return: results of the conversion - a pandas.DataFrame instance
        """
        data = {
            'level': [record.level for record in record_list],
            'type': [record.type.name for record in record_list],
            'alias': [
                record.alias if record.type != LabjournalRecordType.service else None for record in record_list
            ],
            'name': [
                record.name if record.type == LabjournalRecordType.service else None for record in record_list
            ],
            'absolute_datetime': [
                record.datetime.strftime("%Y-%m-%dT%H-%M-%S")
                if record.datetime is not None else None
                for record in record_list
            ],
            'relative_datetime_min': [
                record.relative_time.total_seconds() / self.MINUTE if record.relative_time is not None else None
                for record in record_list
            ],
            'finish_datetime': [
                record.finish_time.strftime("%Y-%m-%dT%H-%M-%S")
                if record.type == LabjournalRecordType.category and record.finish_time is not None else None
                for record in record_list
            ],
            'comments': [record.comments for record in record_list],
        }
        for param in params:
            data[param] = []
            for record in record_list:
                if param in record.customparameters:
                    data[param].append(record.customparameters[param])
                elif param in record.default_values:
                    data[param].append(record.default_values[param])
                else:
                    data[param].append(None)
        record_frame = pandas.DataFrame(
            data=data,
            index=[
                record.path
                if record.type != LabjournalRecordType.service else 'service-%d' % record.id
                for record in record_list
            ],
        )
        return record_frame
