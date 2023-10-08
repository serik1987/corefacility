from django.utils.translation import gettext
from rest_framework import status
from parameterized import parameterized

from .base_test_class import BaseTestClass
from ..project_data_test_mixin import ProjectDataTestMixin


class TestProjectApplication(ProjectDataTestMixin, BaseTestClass):
    """
    Tests lists of the project-to-application links
    """

    __current_project = None

    _request_path = "/api/{version}/projects/{project}/apps/"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_project_data_environment(create_project_application_set=True)

    def setUp(self):
        self._container = self._project_application_set_object.clone()

    @property
    def request_path(self):
        """
        Defines the list request path
        """
        return self._request_path.format(version=self.API_VERSION, project=self.__current_project)

    @parameterized.expand([
        ("hhna", "superuser", status.HTTP_200_OK),
        ("cnl", "superuser", status.HTTP_200_OK),
        ("mnl", "superuser", status.HTTP_200_OK),
        ("mn", "superuser", status.HTTP_200_OK),
        ("nsw", "superuser", status.HTTP_200_OK),
        ("n", "superuser", status.HTTP_200_OK),
        ("nl", "superuser", status.HTTP_200_OK),
        ("gcn", "superuser", status.HTTP_200_OK),
        ("aphhna", "superuser", status.HTTP_200_OK),
        ("cr", "superuser", status.HTTP_200_OK),
        ("n", "user4", status.HTTP_403_FORBIDDEN),
        ("n", "user5", status.HTTP_200_OK),
        ("nsw", "user8", status.HTTP_403_FORBIDDEN),
        ("hhna", "user10", status.HTTP_404_NOT_FOUND),
    ])
    def test_base_search(self, project_alias="hhna", login="superuser", response_status=status.HTTP_200_OK):
        """
        Base retrieval of the project applications
        """
        project = self._project_set_object.get_by_alias(project_alias)
        self.container.filter_by_project(project)
        self.__current_project = project_alias
        self._test_search({"profile": "basic"}, login, response_status)

    def assert_items_equal(self, actual_item, desired_item):
        """
        Compares two list item
        :param actual_item: the item received within the response
        :param desired_item: the item taken from the container
        :return: nothing
        """
        self.assertEquals(actual_item['uuid'], str(desired_item.application.uuid), "Unexpected item UUID")
        self.assertEquals(actual_item['name'], gettext(desired_item.application.name), "Unexpected project name")
        self.assertIn('permissions', actual_item, "The application permissions must be shown in the application list")
        self.assertEquals(actual_item['is_enabled'], desired_item.is_enabled, "Unexpected enability status")
