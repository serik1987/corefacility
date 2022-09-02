from rest_framework import status
from parameterized import parameterized

from core.test.views.field_test.base_test_class import BaseTestClass
from core.test.views.project_data_test_mixin_small import ProjectDataTestMixinSmall
from core.test.views.field_test.data_providers import slug_provider
from imaging import App


def dimensions_data_provider():
    return [
        (name, initial_value, is_valid)
        for name in ("width", "height")
        for initial_value, is_valid in [
            (1e-8, True),
            (0.0, False),
            (-1e-8, False),
            (None, True),
            (1, True),
            ("belbock", False),
        ]
    ]


class TestMapsField(ProjectDataTestMixinSmall, BaseTestClass):
    """
    Tests the field validity for maps
    """

    no_alias_data = {
        "type": "ori",
    }

    no_type_data = {
        "alias": "c023_X210",
    }

    standard_data = {
        "alias": "c023_X210",
        "type": "ori",
    }

    application = App()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_test_environment()
        super().tearDownClass()

    @property
    def resource_name(self):
        return "core/projects/{project_alias}/imaging/data".format(project_alias=self.project.alias)

    def test_alias_required(self):
        """
        Checking whether alias is required field
        """
        self._test_field_required("alias", "no_alias", True, True, None)

    @parameterized.expand(slug_provider(50))
    def test_alias_field(self, initial_value, is_valid):
        """
        Tests the alias field
        """
        self._test_field_value("alias", "standard", initial_value, is_valid, True, initial_value)

    def test_alias_unique(self):
        response1 = self.client.post(self.get_entity_list_path(), {"alias": "c023_X210", "type": "ori"},
                                     format="json", **self.get_authorization_headers("superuser"))
        self.assertEquals(response1.status_code, status.HTTP_201_CREATED, "Unexpected response status")
        response2 = self.client.post(self.get_entity_list_path(), {"alias": "c023_X210", "type": "dir"},
                                     format="json", **self.get_authorization_headers("superuser"))
        self.assertEquals(response2.status_code, status.HTTP_400_BAD_REQUEST,
                          "Alias uniqueness test failed: two maps with the same alias were successfully created")

    def test_type_required(self):
        """
        Tests requireness of the map type
        """
        self._test_field_required("type", "no_type", True, True, None)

    @parameterized.expand([
        ("ori", True),
        ("dir", True),
        ("xxx", False),
        ("", False),
        (None, False),
        (3.14, False),
        (42, False),
    ])
    def test_type_field(self, initial_value, is_valid):
        """
        Tests the requireness of the map type field
        """
        self._test_field_value("type", "standard", initial_value, is_valid, True, initial_value)

    def test_resolution_x(self):
        """
        Tests for the resolution X
        """
        self._test_read_only_field("resolution_x", "standard", None)

    def test_resolution_y(self):
        """
        Tests for the resolution Y
        """
        self._test_read_only_field("resolution_y", "standard", None)

    def test_data(self):
        """
        Tests for the data field
        """
        self._test_read_only_field("data", "standard", None)

    @parameterized.expand([("width",), ("height",)])
    def test_dimensions_required(self, name):
        """
        Tests the requireness of dimensions fields
        """
        self._test_field_required(name, "standard", False, True, None)

    @parameterized.expand(dimensions_data_provider())
    def test_dimensions(self, name, initial_value, is_valid):
        self._test_field_value(name, "standard", initial_value, is_valid, True, initial_value)


del BaseTestClass
