from rest_framework import status
from parameterized import parameterized

from core.test.views.field_test.base_test_class import BaseTestClass
from imaging.tests.views.map_list_mixin import MapListMixin


class TestField(MapListMixin, BaseTestClass):
    """
    Provides test field for pinwheels
    """

    resource_name = "core/projects/test_project/imaging/processors/c022_X100/roi/pinwheels"

    no_x_data = {"y": 240}
    no_y_data = {"x": 100}

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
        ("x", "no_x"),
        ("y", "no_y"),
    ])
    def test_field_required(self, name, initial_data_id):
        self._test_field_required(name, initial_data_id, True, True, None)

    @parameterized.expand([
        (name, "no_%s" % name, initial_data, is_valid)
        for name in ("x", "y")
        for initial_data, is_valid in [
            (1024, True),
            (1, True),
            (0, True),
            (-1, False),
            ("this is a string", False),
            (None, False),
            (3.14, False),
        ]
    ])
    def test_field_value(self, name, initial_data_id, initial_value, is_valid):
        self._test_field_value(name, initial_data_id, initial_value, is_valid, True, initial_value)


del BaseTestClass
