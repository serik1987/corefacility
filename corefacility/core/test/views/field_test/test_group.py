from parameterized import parameterized

from .base_test_class import BaseTestClass
from .data_providers import arbitrary_string_provider


class TestGroup(BaseTestClass):
    """
    Checks the validity of the group fields
    """

    empty_data = {}
    standard_data = {"name": "Оптическое картирование"}

    resource_name = "groups"

    def test_name_required(self):
        self._test_field_required("name", "empty", True, True, "Some group name")

    @parameterized.expand(arbitrary_string_provider(False, 256))
    def test_name(self, group_name, is_valid):
        self._test_field_value("name", "empty", group_name, is_valid, True, group_name)

    def test_governor_read_only(self):
        self._test_read_only_field("name", "standard", None)
