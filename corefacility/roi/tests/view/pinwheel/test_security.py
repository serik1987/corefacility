from rest_framework import status
from parameterized import parameterized

from core.test.views.security_test.base_test_class import BaseTestClass
from imaging.tests.views.map_list_mixin import MapListMixin
from roi.entity import Pinwheel


def pinwheel_modification_provider(success_status=status.HTTP_201_CREATED):
    return [
        ("data_view", 0, "test_project1", status.HTTP_403_FORBIDDEN),
        ("full", 0, "test_project", success_status),
        ("data_process", 0, "test_project", success_status),
        ("full", 1, "test_project1", success_status),
        ("superuser", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_full", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_view", 1, "test_project", status.HTTP_403_FORBIDDEN),
        ("data_full", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("superuser", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("no_access", 1, "test_project1", status.HTTP_404_NOT_FOUND),
        ("data_process", 1, "test_project1", success_status),
        ("no_access", 0, "test_project", status.HTTP_404_NOT_FOUND),
    ]


def pinwheel_view_provider():
    return [
        ("data_view", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("full", 0, "test_project", status.HTTP_200_OK),
        ("data_process", 0, "test_project", status.HTTP_200_OK),
        ("full", 1, "test_project1", status.HTTP_200_OK),
        ("superuser", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_full", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_view", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_full", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("superuser", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("no_access", 1, "test_project1", status.HTTP_404_NOT_FOUND),
        ("data_process", 1, "test_project1", status.HTTP_200_OK),
        ("no_access", 0, "test_project", status.HTTP_404_NOT_FOUND),
    ]


def pinwheel_delete_provider():
    return [
        ("data_view", 0, "test_project1", status.HTTP_403_FORBIDDEN),
        ("full", 0, "test_project", status.HTTP_204_NO_CONTENT),
        ("data_process", 0, "test_project", status.HTTP_403_FORBIDDEN),
        ("full", 1, "test_project1", status.HTTP_204_NO_CONTENT),
        ("superuser", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_full", 1, "test_project", status.HTTP_404_NOT_FOUND),
        ("data_view", 1, "test_project", status.HTTP_403_FORBIDDEN),
        ("data_full", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("superuser", 0, "test_project1", status.HTTP_404_NOT_FOUND),
        ("no_access", 1, "test_project1", status.HTTP_404_NOT_FOUND),
        ("data_process", 1, "test_project1", status.HTTP_403_FORBIDDEN),
        ("no_access", 0, "test_project", status.HTTP_404_NOT_FOUND),
    ]


class TestSecurity(MapListMixin, BaseTestClass):
    """
    Provides security tests for pinwheels
    """

    PINWHEEL_LIST_PATH = "/api/{version}/core/projects/{project}/imaging/processors/{map}/roi/pinwheels/"

    _tested_entity = Pinwheel

    alias_field = None

    default_data = {
        "x": 100,
        "y": 240
    }

    updated_data = {
        "x": 200,
    }

    current_project = None
    current_map = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment(add_roi_application=True)

    def setUp(self):
        super().setUp()
        self.initialize_projects()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_test_environment()
        super().tearDownClass()

    @property
    def resource_name(self):
        return "core/projects/{project}/imaging/processors/{map}/roi/pinwheels".format(
            project=self.current_project.alias,
            map=self.current_map.alias
        )

    @parameterized.expand(pinwheel_modification_provider())
    def test_entity_create(self, login, project_index, map_location, expected_status_code):
        """
        Tests the API for pinwheel create
        :param login: login of the user that tries to create the pinwheel
        :param project_index: 0 for test_project, 1 for test_project1
        :param map_location: alias of the project to which map the user tries to attach the pinwheel
        :param expected_status_code: the response code given that the test is successful
        """
        self.set_current_project_and_map(project_index, map_location)
        self._test_entity_create("default", login, expected_status_code)

    @parameterized.expand(pinwheel_view_provider())
    def test_entity_get(self, login, project_index, map_location, expected_status_code):
        """
        Tries API for the pinwheel retrieve
        :param login: login of the user that tries to create the pinwheel
        :param project_index: 0 for test_project, 1 for test_project1
        :param map_location: alias of the project to which map the user tries to attach the pinwheel
        :param expected_status_code: the response code given that the test is successful
        """
        self.set_current_project_and_map(project_index, map_location)
        self._test_entity_get("default", login, expected_status_code)

    @parameterized.expand(pinwheel_modification_provider(success_status=status.HTTP_200_OK))
    def test_entity_update(self, login, project_index, map_location, expected_status_code):
        """
        Tries to update the map info
        :param login: login of the user that tries to create the pinwheel
        :param project_index: 0 for test_project, 1 for test_project1
        :param map_location: alias of the project to which map the user tries to attach the pinwheel
        :param expected_status_code: the response code given that the test is successful
        """
        self.set_current_project_and_map(project_index, map_location)
        self._test_entity_update("default", "updated", login, expected_status_code)

    @parameterized.expand(pinwheel_modification_provider(success_status=status.HTTP_200_OK))
    def test_entity_partial_update(self, login, project_index, map_location, expected_status_code):
        """
        Tries to update the map info partially
        :param login: login of the user that tries to create the pinwheel
        :param project_index: 0 for test_project, 1 for test_project1
        :param map_location: alias of the project to which map the user tries to attach the pinwheel
        :param expected_status_code: the response code given that the test is successfully
        """
        self.set_current_project_and_map(project_index, map_location)
        self._test_entity_partial_update("default", "updated", login, expected_status_code)

    @parameterized.expand(pinwheel_delete_provider())
    def test_entity_delete(self, login, project_index, map_location, expected_status_code):
        """
        Tries to delete the map
        :param login: login of the user that tries to create the pinwheel
        :param project_index: 0 for test_project, 1 for test_project1
        :param map_location: alias of the project to which map the user tries to attach the pinwheel
        :param expected_status_code: the response code given that the test is successfuls
        """
        self.set_current_project_and_map(project_index, map_location)
        self._test_entity_destroy("default", login, expected_status_code)

    def set_current_project_and_map(self, project_index, map_location):
        """
        Sets current location of the project and map
        :param project_index: index for the current project
        :param map_location: alias of a project that contains the current map
        """
        self.current_project = self.projects[project_index]
        self.current_map = self.project_maps[map_location][0]

    def create_entity_for_test(self, test_data):
        """
        Creates the entity for testing purpose
        :param test_data: The data that shall be assigned to fields of the creating entity
        :return: ID of the newly created entity
        """
        test_data['map'] = self.current_map
        return super().create_entity_for_test(test_data)

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info
        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        expected_info = expected_info.copy()
        if "map" in expected_info:
            del expected_info['map']
        super().check_detail_info(actual_info, expected_info)


del BaseTestClass
