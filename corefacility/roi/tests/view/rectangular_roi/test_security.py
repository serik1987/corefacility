from rest_framework import status
from parameterized import parameterized

from core.test.views.security_test.base_test_class import BaseTestClass
from imaging.tests.views.map_list_mixin import MapListMixin
from roi.entity import RectangularRoi


class TestRectangularRoiSecurity(MapListMixin, BaseTestClass):
    """
    Security test for the rectangular ROI
    """

    default_data = {"left": 100, "right": 200, "top": 150, "bottom": 350}
    updated_data = {"bottom": 400}

    _tested_entity = RectangularRoi
    alias_field = None

    resource_template = "core/projects/{project}/imaging/processors/{map}/roi/rectangular"
    full_template = "/api/{version}/" + resource_template + "/"
    resource_name = resource_template.format(project="test_project", map="c022_X210")

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

    @parameterized.expand([
        ("superuser", status.HTTP_201_CREATED),
        ("full", status.HTTP_201_CREATED),
        ("data_full", status.HTTP_201_CREATED),
        ("data_process", status.HTTP_201_CREATED),
        ("data_view", status.HTTP_403_FORBIDDEN),
        ("no_access", status.HTTP_404_NOT_FOUND),
        ("ordinary_user", status.HTTP_404_NOT_FOUND),
        (None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_create(self, alias, response_code):
        super()._test_entity_create("default", alias, response_code)

    def test_entity_create_negative(self):
        request_path = self.full_template.format(version=self.API_VERSION, project="test_project1", map="c022_X210")
        headers = self.get_authorization_headers("superuser")
        response = self.client.post(request_path, self.default_data, format="json", **headers)
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    @parameterized.expand([
        ("superuser", status.HTTP_200_OK),
        ("full", status.HTTP_200_OK),
        ("data_full", status.HTTP_200_OK),
        ("data_process", status.HTTP_200_OK),
        ("data_view", status.HTTP_200_OK),
        ("no_access", status.HTTP_404_NOT_FOUND),
        ("ordinary_user", status.HTTP_404_NOT_FOUND),
        (None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_get(self, alias, response_code):
        super()._test_entity_get("default", alias, response_code)

    @parameterized.expand([
        ("superuser", status.HTTP_200_OK),
        ("full", status.HTTP_200_OK),
        ("data_full", status.HTTP_200_OK),
        ("data_process", status.HTTP_200_OK),
        ("data_view", status.HTTP_403_FORBIDDEN),
        ("no_access", status.HTTP_404_NOT_FOUND),
        ("ordinary_user", status.HTTP_404_NOT_FOUND),
        (None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_update(self, alias, response_code):
        super()._test_entity_update("default", "updated", alias, response_code)

    @parameterized.expand([
        ("superuser", status.HTTP_200_OK),
        ("full", status.HTTP_200_OK),
        ("data_full", status.HTTP_200_OK),
        ("data_process", status.HTTP_200_OK),
        ("data_view", status.HTTP_403_FORBIDDEN),
        ("no_access", status.HTTP_404_NOT_FOUND),
        ("ordinary_user", status.HTTP_404_NOT_FOUND),
        (None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_partial_update(self, alias, response_code):
        super()._test_entity_partial_update("default", "updated", alias, response_code)

    @parameterized.expand([
        ("superuser", status.HTTP_204_NO_CONTENT),
        ("full", status.HTTP_204_NO_CONTENT),
        ("data_full", status.HTTP_204_NO_CONTENT),
        ("data_process", status.HTTP_403_FORBIDDEN),
        ("data_view", status.HTTP_403_FORBIDDEN),
        ("no_access", status.HTTP_404_NOT_FOUND),
        ("ordinary_user", status.HTTP_404_NOT_FOUND),
        (None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_destroy(self, alias, response_code):
        super()._test_entity_destroy("default", alias, response_code)

    def create_entity_for_test(self, test_data):
        """
        Creates the entity for testing purpose
        :param test_data: The data that shall be assigned to fields of the creating entity
        :return: ID of the newly created entity
        """
        test_data = test_data.copy()
        test_data['map'] = self.project_maps['test_project'][0]
        return super().create_entity_for_test(test_data)

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info
        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        for field_name in ("id", "left", "right", "top", "bottom"):
            if field_name in expected_info:
                actual_value = self.get_actual_value(actual_info, field_name)
                expected_value = expected_info[field_name]
                self.assertEquals(actual_value, expected_value,
                                  "Unexpected value of the '{field}' field".format(field=field_name))
