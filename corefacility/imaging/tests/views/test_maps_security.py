from rest_framework import status
from parameterized import parameterized

from core.test.views.security_test.base_project_data_view_test import BaseProjectDataViewTest \
    as BaseProjectDataSecurityTest
from imaging import App
from imaging.entity import Map


class TestMapsSecurity(BaseProjectDataSecurityTest):
    """
    Provides security tests for functional maps
    """

    resource_name = "core/projects/test_project/imaging/data"
    """ The URL path segment between the '/api/{version}/' and '/{resource-id}/' parts. """

    _tested_entity = Map
    """ Class of the entity to test """

    default_data = {
            "alias": "c023_X210",
            "type": "ori",
            "width": 12400.0,
            "height": 12400.0,
        }

    updated_data = {
        "width": 10000.0,
        "height": 10000.0,
    }

    data_process_status = status.HTTP_403_FORBIDDEN
    """
    Defines the status code when the user tries to post, put or patch the data under 'data_process' permission
    """

    application = None
    """ Application to be tested """

    @classmethod
    def setUpTestData(cls):
        cls.application = App()
        super().setUpTestData()

    def create_entity_for_test(self, test_data):
        """
        Creates the entity for testing purpose

        :param test_data: The data that shall be assigned to fields of the creating entity
        :return: ID of the newly created entity
        """
        if "project" not in test_data:
            test_data = test_data.copy()
            test_data['project'] = self.project
        return super().create_entity_for_test(test_data)


del BaseProjectDataSecurityTest
