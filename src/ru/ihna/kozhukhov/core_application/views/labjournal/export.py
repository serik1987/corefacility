import os
import re
import tempfile
from io import BytesIO
from pathlib import Path
import urllib.parse

from django.http import FileResponse
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from ru.ihna.kozhukhov.core_application.entity.labjournal_record.complex_interval import ComplexInterval
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType

from .base_category import BaseCategoryView
from .exporters import find_exporter_for


class ExportView(BaseCategoryView):
    """
    Exports the category to json or csv.

    The export process takes several stages. The exported information is located in a special temporary file between
    the stages. After successful completion of all export stages such a temporary file will be deleted automatically.
    Also, this is assumed that such temporary files will be periodically cleaned by the operating system.
    """

    TEMPORARY_FILE_PARTS = 3
    """ Number of minimum parts inside the temporary file that contains information about the user and the project """

    MAX_FILE_SIZE = 500 * 1024 * 1024
    """ All files exceeding 500 Mb will be downloaded directly and will not be remove after the download. """

    temporary_file_pattern = re.compile(r'^[^\\/]+$')
    """ Let's exclude \ and / characters in order to avoid hacker attacks """

    ACTION_EXPORT = 'export'
    """ The export action """

    ACTION_CHILD_URLS = 'child-links'
    """ The child links action """

    ACTION_DOWNLOAD = 'download'
    """ The download action """

    SUPPORTED_ACTIONS = [ACTION_EXPORT, ACTION_CHILD_URLS, ACTION_DOWNLOAD]
    """ All actions supported by this view """

    _search_on_relative_date_when_reference_date_is_none = True
    """
    If False, the view will throw the ValidationError when either date_from_relative or date_to_relative filters is ON
    and parent category doesn't have its own datetime.
    If True, the view will return an empty record set in this case
    """

    _temporary_file_short = None
    """ A short name of the temporary file """

    _temporary_file = None
    """ An absolute path to the temporary file """

    _action = None
    """ What action to do """

    _depth = None
    """
    Nesting depth that is equal to zero means that the content of child categories will not be exported.
    If nesting depth is n, the content of child categories will be exported with nesting depth equal to n-1.
    If nesting depth is None, all descendant records will be exported.
    """

    _params = None
    """ List of all custom parameters to export """

    _page = None
    """ Number of a page to export """

    def list(self, request, *args, filename=None, export_format=None, **kwargs):
        """
            The main function to export to JSON or CSV

            :param request: the HTTP request received from the user
            :param args: useless
            :param filename: name of an output file
            :param export_format: the format to be exported
            :param kwargs: useless
            :return: the HTTP response
        """
        self._parse_query_params(request.query_params)
        if self._action == self.ACTION_EXPORT:
            record_set = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(record_set)
            exporter = find_exporter_for(self, request, export_format)
            self._update_temporary_file(exporter, page)
            return self._get_response([
                self._get_next_page_link(),
                self._get_record_list_links(),
            ])
        elif self._action == self.ACTION_CHILD_URLS:
            record_set = self._get_categories_with_datetime()
            page = self.paginate_queryset(record_set)
            return self._get_response([
                self._get_next_page_link(),
                *self._get_category_export_link(request, page, filename, export_format, kwargs),
            ])
        elif self._action == self.ACTION_DOWNLOAD:
            self._generate_full_temporary_filename()
            if os.path.getsize(self._temporary_file) > self.MAX_FILE_SIZE:
                output_file = open(self._temporary_file, 'rb')
                return FileResponse(output_file,
                                    as_attachment=True,
                                    filename="%s.%s" % (filename, export_format)
                                    )
            else:
                with open(self._temporary_file, 'rb') as output_file:
                    output_stream = BytesIO(output_file.read())
                os.unlink(self._temporary_file)
                return FileResponse(output_stream,
                                    as_attachment=True,
                                    filename="%s.%s" % (filename, export_format)
                                    )
        else:
            raise RuntimeError("Unreachable code has reached")

    def _parse_query_params(self, query_params):
        """
        Parses query params that are not related to filtration routines.

        :param query_params: query params to validate
        """
        errors = dict()
        self._temporary_file = None
        self._temporary_file_short = query_params.get('tmp_file', None)
        if self._temporary_file_short is not None and not self.temporary_file_pattern.match(self._temporary_file_short):
            errors['tmp_file'] = "Name of the temporary file contains prohibited characters."
        self._action = query_params.get('action', 'export').lower()
        if self._action not in self.SUPPORTED_ACTIONS:
            errors['action'] = "The action is invalid or unsupported."
        try:
            self._page = int(query_params.get('page', 1))
        except ValueError:
            errors['action'] = "Bad page number."
        if self._page is not None and self._page < 1:
            errors['page'] = "The page number is too low."
        try:
            self._depth = query_params.get('depth', None)
            if self._depth is not None:
                self._depth = int(self._depth)
        except ValueError:
            errors['depth'] = "Bad number of depth."
        if self._depth is not None and self._depth < 0:
            errors['depth'] = "The depth can't be negative."
        self._params = query_params.get('params', '')
        if len(self._params) > 0:
            self._params = self._params.split(',')
        else:
            self._params = list()
        if len(errors) > 0:
            raise ValidationError(errors)

    def _update_temporary_file(self, exporter, page):
        """
        Updates the temporary file using the file exporter.
        Name of the temporary file must be given by the client application using the 'tmp_file' query parameter.
        If the temporary file is not given by the client application, new temporary file will be created.
        Name of the temporary file must contain information about a current project and a current user. In case when
        this is not true, a 400th response will be generated.
        If the temporary file does not exist, a 400th response will be generated.

        :param exporter: the exporter object that will be used to create/update a temporary file
        :param page: a list of labjournal records
        """
        if self._temporary_file_short is None:
            self._temporary_file = exporter.create_new_frame(page, self._params)
            self._temporary_file_short = str(Path(self._temporary_file).name)
        else:
            self._generate_full_temporary_filename()
            exporter.extend_existent_frame(self._temporary_file, page, self._params)

    def _generate_full_temporary_filename(self):
        """
        Generates an absolute path to the temporary file.
        Also, checks that such a file exists and checks the user has permissions to access the file.
        """
        try:
            application_name, user_login, project_alias, _ = \
                self._temporary_file_short.split('.', self.TEMPORARY_FILE_PARTS)
        except ValueError:
            raise ValidationError({'tmp_file': "Bad format of the validation file"})
        if application_name != 'corefacility' or user_login != self.request.user.login \
                or project_alias != self.request.project.alias:
            raise ValidationError({'tmp_file': "The filename doesn't relate to this project or user"})
        self._temporary_file = os.path.join(tempfile.gettempdir(), self._temporary_file_short)
        if not os.path.isfile(self._temporary_file):
            raise ValidationError({'tmp_file': 'The temporary file does not exist.'})

    def _get_next_page_link(self):
        """
        Inserts the URL for the next page, in case of necessity

        :return: URL for the next page link or None if the last page has reached
        """
        next_page_url = self.paginator.get_next_link()
        if next_page_url is not None:
            next_page_link = replace_query_param(next_page_url, 'tmp_file', self._temporary_file_short)
        else:
            next_page_link = None
        return next_page_link

    def _get_record_list_links(self):
        """
        Constructs a links to the request for links of exporting all child records
        """
        categories_with_datetime_set = self._get_categories_with_datetime()
        if self._page == 1 and len(categories_with_datetime_set) > 0 and (self._depth is None or self._depth > 0):
            base_uri = self.request.build_absolute_uri()
            child_list_uri = replace_query_param(base_uri, 'action', 'child-links')
            child_list_uri = replace_query_param(child_list_uri, 'tmp_file', self._temporary_file_short)
            if self._depth is not None:
                child_list_uri = replace_query_param(child_list_uri, 'depth', self._depth - 1)
        else:
            child_list_uri = None
        return child_list_uri

    def _get_category_export_link(self, request, category_list, filename, export_format, kwargs):
        """
        Returns list of URLs that are used for export of child categories

        :param request: the request received from the client
        :param category_list: list of all categories that have child records to be exported
        :param filename: the desired filename to be exported
        :param export_format: format of the output data
        :param kwargs: all other keyword arguments revealed from parsing the request path
        :return: list of URLs that the client application shall follow in order to export all child record for given
            categories
        """
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(request.build_absolute_uri())
        query_params = urllib.parse.parse_qs(query)
        query_params['action'] = ['export']
        if 'page' in query_params:
            del query_params['page']
        query = urllib.parse.urlencode(query_params, doseq=True)
        url_list = list()
        for category in category_list:
            path = "/api/v{version}/projects/{project}/labjournal/categories/{category}/{filename}.{export_format}" \
            .format(
                project=request.project.id,
                category=category.id,
                filename=filename,
                export_format=export_format,
                **kwargs,
            )
            url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
            url_list.append(url)
        return url_list

    def _get_categories_with_datetime(self):
        """
        Returns list of all categories which datetime is not None.
        This method can be used for listing all records that have child record: a record has child records if and only
        if it is category and its datetime is not zero.
        """
        categories_with_datetime_set = self.get_queryset()
        categories_with_datetime_set.type = LabjournalRecordType.category
        categories_with_datetime_set.datetime = ComplexInterval(-float('inf'), float('inf'))
        return categories_with_datetime_set

    def _get_response(self, url_list):
        """
        Returns the response

        :param url_list: list of URL that the client must follow in order to accomplish the export process
        :return the response itself
        """
        return Response({
            'tmp_file': self._temporary_file_short,
            'next_links': [url for url in url_list if url is not None],
        })
