import math
import urllib3
import json

from django.utils.translation import gettext_lazy as _
from rest_framework import status

from ru.ihna.kozhukhov.core_application.modules.sync_full_mode import FullModeSynchronization
from .ihna_employees_serializer import IhnaEmployeesSerializer
from ru.ihna.kozhukhov.core_application.exceptions.synchronization_exceptions import RemoteServerError


class IhnaSynchronization(FullModeSynchronization):
    """
    Provides synchronization through the IHNA website for demonstration and testing
    """

    DEFAULT_REQUEST_METHOD = "GET"
    DEFAULT_IHNA_WEBSITE = "https://www.ihna.ru"
    DEFAULT_USER_LIST_PATH = "/ppage2/api/user-list"
    DEFAULT_LANG = "ru"
    DEFAULT_PROFILE = "basic"
    DEFAULT_PAGE_LENGTH = 20

    _http_client = None
    """ The urllib3 client """

    _total_count = None
    """ Total number of users downloaded during the last request """

    def get_serializer_class(self):
        """
        Defines the serializer class. The serializer class is used to represent module settings in JSON format
        :return: instance of rest_framework.serializers.Serializer class
        """
        return IhnaEmployeesSerializer

    def get_pseudomodule_identity(self):
        """
        If the module is pseudo-module, the function returns some short string that is required for the frontend to
        identify the pseudo-module.
        :return: a string containing the pseudo-module identity
        """
        return "ihna_employees"

    @staticmethod
    def validate_page_number(page_number):
        """
        Checks that the page number is positive integer
        :param page_number: the page number of string representation of the page number
        :return: the page number or 0 if page number is not valid
        """
        try:
            page_number = int(page_number)
            if page_number < 0:
                page_number = 0
        except ValueError:
            page_number = 0
        return page_number

    @property
    def http_client(self):
        """
        At first call, the function creates urllib3.PoolManager object.
        At each subsequent call the function gets the previously created urllib3.PoolManager object
        :return: the urllib3.PoolManager object
        """
        if self._http_client is None:
            self._http_client = urllib3.PoolManager()
        return self._http_client

    @property
    def app_class(self):
        """
        Returns the application class
        """
        return "ru.ihna.kozhukhov.core_application.modules.sync_ihna_employee.IhnaSynchronization"

    def get_alias(self):
        """
        The application alias

        :return: alias
        """
        return "ihna_employees"

    def get_name(self):
        """
        The synchronization name

        :return: the synchronization name
        """
        _("IHNA RAS account synchronization")
        return "IHNA RAS account synchronization"

    def get_ihna_website(self):
        """
        Returns the URL address for the IHNA website

        :return: the URL address
        """
        return self.user_settings.get("ihna_website", self.DEFAULT_IHNA_WEBSITE)

    def get_language(self):
        """
        Returns the currently working language

        :return: the currently working language. Allowed values: 'ru', 'en'
        """
        return self.user_settings.get("language", self.DEFAULT_LANG)

    def get_page_length(self):
        """
        Returns the page size

        :return: the page size
        """
        return self.user_settings.get("page_length", self.DEFAULT_PAGE_LENGTH)

    def get_raw_data(self, page_number=0, **options):
        """
        Makes an HTTP request to the ihna.ru website and downloads some portion of the user list from the site

        :param page_number: number of a page
        :param options: Some extra options that will be ignored
        :return: the raw user list response (to be put into the following functions)
        """
        url = self.get_ihna_website() + self.DEFAULT_USER_LIST_PATH
        page_number = self.validate_page_number(page_number)
        query_params = {
            "lang": self.get_language(),
            "profile": self.DEFAULT_PROFILE,
            "page_length": self.get_page_length(),
            "page_number": page_number
        }
        response = self.http_client.request(self.DEFAULT_REQUEST_METHOD, url, fields=query_params)
        if response.status != status.HTTP_200_OK:
            raise RemoteServerError()
        try:
            response_body = json.loads(response.data.decode("utf-8"))
            if response_body['result'] != "success":
                raise RuntimeError("The result is not success")
        except Exception as err:
            raise RemoteServerError()
        self._total_count = response_body['output']['count']
        return response_body['output']

    def get_download_total_steps(self):
        """
        Estimates the total number of steps required for downloading.
        :return: the total number of steps
        """
        return math.ceil(self._total_count / self.get_page_length())

    def find_user(self, raw_data, **options):
        """
        Finds all users in the raw data

        :param raw_data: the raw data returned by the get_raw_data function
        :param options: some request options
        :return: the generator that allows to iterate over (login, user_kwargs) tuples. login is used for searching
            over all users while user_kwargs will during the user create if no user has been found
        """
        for user_info in raw_data['data']:
            user_kwargs = {
                "surname": user_info['surname'],
                "name": user_info['first_name'],
                "login": user_info['string_id'],
            }
            yield user_kwargs['login'], user_kwargs

    def get_next_options(self, raw_data, page_number=0, **options):
        """
        If downloading occurs in a single stage the function always return True. Otherwise it returns True if
        raw_data correspond to the last stage of account downloading

        :param raw_data: the raw data itself
        :param page_number: number of a page
        :param options: some additional options
        :return: True or False
        """
        try:
            next_page = self.validate_page_number(page_number) + 1
            page_length = self.get_page_length()
            total_count = int(raw_data['count'])
            if next_page * page_length > total_count:
                new_options = None
            else:
                new_options = {"page_number": next_page, **options}
            return new_options
        except Exception as err:
            raise RemoteServerError()
