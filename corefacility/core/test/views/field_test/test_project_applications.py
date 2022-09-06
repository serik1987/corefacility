from imaging import App as ImagingApp
from parameterized import parameterized

from .data_providers import boolean_provider
from .base_test_class import BaseTestClass
from ..project_data_test_mixin import ProjectDataTestMixin


class TestProjectApplications(ProjectDataTestMixin, BaseTestClass):
    """
    Provides testing of quality of field validations for the ProjectApplicationViewSet
    """

    id_field = "uuid"

    is_enabled_data = {"is_enabled": True}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_project_data_environment()

    @property
    def resource_name(self):
        return "projects/nsw/apps"

    @property
    def uuid_data(self):
        return {"uuid": str(ImagingApp().uuid)}

    def test_is_enabled_required(self):
        """
        Tests whether 'is_enabled' is required field
        """
        self._test_field_required("is_enabled", "uuid", True, True, None)

    @parameterized.expand(boolean_provider())
    def test_is_enabled_value(self, initial_value, is_valid):
        """
        tests whether 'is_enabled' field has been properly validated
        """
        self._test_field_value("is_enabled", "uuid", initial_value, is_valid, True, initial_value)

    def test_uuid_required(self):
        """
        Tests whether the uuid field is required
        """
        self._test_field_required("uuid", "is_enabled", True, False, None)

    def test_invalid_uuid(self):
        self._test_field_value("uuid", "is_enabled", "some invalid uuid", False, None, None)
