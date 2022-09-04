from rest_framework import status
from parameterized import parameterized

from core.test.views.field_test.base_test_class import BaseTestClass
from imaging.tests.views.map_list_mixin import MapListMixin


def field_provider():
    return [
        ("left", "no_left"),
        ("right", "no_right"),
        ("top", "no_top"),
        ("bottom", "no_bottom"),
    ]


def field_value_provider():
    return [
        (name, initial_data_id, initial_value, is_valid)
        for name, initial_data_id in field_provider()
        for initial_value, is_valid in [
            (1, True),
            (0, True),
            (-1, False),
            ("sample string", False),
            (True, False),
            (None, False),
        ]
    ]


def rectangle_provider():
    return [
        (100, 101, 200, 201, True),
        (100, 100, 200, 201, False),
        (100, 99, 200, 201, False),
        (100, 101, 200, 200, False),
        (100, 101, 200, 199, False),
    ]


class TestRectangularRoiFields(MapListMixin, BaseTestClass):
    """
    Tests the map list mixin
    """

    no_left_data = {"right": 200, "top": 150, "bottom": 350}
    no_right_data = {"left": 100, "top": 150, "bottom": 350}
    no_top_data = {"left": 100, "right": 200, "bottom": 350}
    no_bottom_data = {"left": 100, "right": 200, "top": 150}

    resource_name = "core/projects/test_project/imaging/processors/c022_X210/roi/rectangular"
    
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

    @parameterized.expand(field_provider())
    def test_field_required(self, name, initial_data_id):
        """
        Field requiring test
        """
        self._test_field_required(name, initial_data_id, True, True, None)

    @parameterized.expand(field_value_provider())
    def test_field_value(self, name, initial_data_id, initial_value, is_valid):
        """
        Field validation test
        """
        if (name == "bottom" or name == "right") and is_valid:
            return
        self._test_field_value(name, initial_data_id, initial_value, is_valid, True, initial_value)

    @parameterized.expand(rectangle_provider())
    def test_field_combination(self, left, right, top, bottom, is_valid):
        """
        Tests whether the user can enter invalid combination of valid field values
        """
        input_data = {
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
        }
        headers = self.get_authorization_headers("superuser")
        response = self.client.post(self.get_entity_list_path(), input_data, format="json", **headers)
        if is_valid:
            self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
