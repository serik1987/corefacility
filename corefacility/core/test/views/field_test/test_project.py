from parameterized import parameterized

from .base_test_class import BaseTestClass
from .data_providers import slug_provider


class TestProject(BaseTestClass):
    """
    Provides field validation tests for single projects
    """

    resource_name = "projects"

    no_alias_data = {
        "name": "Some project",
        "root_group_id": None,
        "root_group_name": "Some project group"
    }

    # @parameterized.expand(slug_provider(64))
    # def test_alias_valid(self, alias_value, is_valid):
    #     """
    #     Checks the project alias validation feature
    #
    #     :param alias_value: tested value
    #     :param is_valid: True is such an alias is valid, False otherwise
    #     :return: nothing
    #     """
    #     self._test_field_value("alias", "no_alias", alias_value, is_valid, True, alias_value)

    def test_alias_valid(self):
        self._test_field_value("alias", "no_alias", "vasomotor-oscillations", True, True, "vasomotor-oscillations")
