import re
import json

from bs4 import BeautifulSoup
from rest_framework import status


class PageObject:
    """
    This is a compact representation of the main page
    """

    _web_page = None
    _client_settings = None

    SETTINGS_TEMPLATE = re.compile(r'^window\.SETTINGS\s*=\s*(.+)\s*;\s*$')

    def __init__(self, test, response):
        """
        Initializes the main page object

        :param test: a test that has been called the page object
        :param response: response that contains the main page
        """
        test.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected response status for the UI response")
        self._web_page = BeautifulSoup(response.rendered_content, "html.parser")

    def get_option(self, name: str):
        """
        Parses and returns the client option

        :param name: name of the client option
        :return: nothing
        """
        if self._client_settings is None:
            self.render_client_settings()
        if name in self._client_settings:
            value = self._client_settings[name]
        else:
            value = None
        return value

    def render_client_settings(self):
        self._client_settings = {}
        settings_script = self._web_page.head.find("script").text.strip()
        match = self.SETTINGS_TEMPLATE.match(settings_script)
        settings_data = match[1]
        self._client_settings = json.loads(settings_data)
