from ru.ihna.kozhukhov.core_application.exceptions.api_exceptions import BadExportFormatException

from .pandas_exporter import PandasExporter
from .csv_exporter import CsvExporter

__all_exporters = {
    'json': PandasExporter,
    'csv': CsvExporter,
}

def find_exporter_for(view, request, export_format):
    """
    Finds a proper exporter for a specific export format.
    Exporter is a special class that implements basic routines connected with data exporting.

    :param view: a view that wants new exporter
    :param request: an HTTP request that has created such a view
    :param export_format: the export format as it is specified by the HTTP request path.
    :return: the exporter object: an instance of the Exporter class
    """
    try:
        return __all_exporters[export_format](request, view)
    except KeyError:
        raise BadExportFormatException()
