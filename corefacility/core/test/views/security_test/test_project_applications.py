from uuid import UUID
from rest_framework import status
from parameterized import parameterized

from core.entity.corefacility_module import CorefacilityModuleSet
from core.entity.project_application import ProjectApplication, ProjectApplicationSet
from core import App as CoreApp
from imaging import App as ImagingApp
from roi import App as RoiApp
from .base_test_class import BaseTestClass
from ..project_data_test_mixin import ProjectDataTestMixin


class TestProjectApplications(ProjectDataTestMixin, BaseTestClass):
    """
    Tests the project applications
    """

    _tested_entity = ProjectApplication
    resource_name = "projects/nsw/apps"
    project = None
    ordinary_user_required = False

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_project_data_environment()
        cls.project = cls._project_set_object.get_by_alias("nsw")

    @property
    def imaging_enabled_data(self):
        return {"uuid": str(ImagingApp().uuid), "is_enabled": True}

    @property
    def disabled_application_data(self):
        imaging = ImagingApp()
        imaging.is_enabled = False
        imaging.update()
        return {"uuid": str(imaging.uuid), "is_enabled": True}

    @property
    def imaging_disabled_data(self):
        return {"uuid": str(ImagingApp().uuid), "is_enabled": False}

    @property
    def roi_enabled_data(self):
        return {"uuid": str(RoiApp().uuid), "is_enabled": True}

    @property
    def fake_application_data(self):
        return {"uuid": "c75b9bd9-51bb-4891-9aed-2ca1bb3f6083", "is_enabled": True}

    @property
    def core_application_data(self):
        return {"uuid": str(CoreApp().uuid), "is_enabled": True}

    @parameterized.expand([
        ("imaging_enabled", "superuser", status.HTTP_201_CREATED),
        ("imaging_disabled", "superuser", status.HTTP_201_CREATED),
        ("roi_enabled", "superuser", status.HTTP_201_CREATED),
        ("core_application", "superuser", status.HTTP_400_BAD_REQUEST),
        ("fake_application", "superuser", status.HTTP_400_BAD_REQUEST),
        ("disabled_application", "superuser", status.HTTP_400_BAD_REQUEST),
        ("imaging_enabled", "user5", status.HTTP_201_CREATED),
        ("imaging_disabled", "user5", status.HTTP_400_BAD_REQUEST),
        ("roi_enabled", "user5", status.HTTP_201_CREATED),
        ("core_application", "user5", status.HTTP_400_BAD_REQUEST),
        ("fake_application", "user5", status.HTTP_400_BAD_REQUEST),
        ("imaging_enabled", "user6", status.HTTP_403_FORBIDDEN),
        ("imaging_disabled", "user6", status.HTTP_403_FORBIDDEN),
        ("roi_enabled", "user6", status.HTTP_403_FORBIDDEN),
        ("core_application", "user6", status.HTTP_403_FORBIDDEN),
        ("fake_application", "user6", status.HTTP_403_FORBIDDEN),
        ("imaging_enabled", "user1", status.HTTP_404_NOT_FOUND),
        ("imaging_disabled", "user1", status.HTTP_404_NOT_FOUND),
        ("roi_enabled", "user1", status.HTTP_404_NOT_FOUND),
        ("core_application", "user1", status.HTTP_404_NOT_FOUND),
        ("fake_application", "user1", status.HTTP_404_NOT_FOUND),
        # 21 tests
    ])
    def test_entity_create(self, data_id, token_id, expected_status_code):
        """
        Security test for the entity create
        :param data_id: defines the input data and the pre-test operations (e.g., enabling of disabling operations etc.)
        :param token_id: login of a user truing to add the data
        :param expected_status_code: the response status that should be
        """
        response = super()._test_entity_create(data_id, token_id, expected_status_code)
        print(token_id, data_id, response)
        print(response.data)

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info
        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        self.assertEquals(actual_info['uuid'], expected_info['uuid'], "The application UUIDs are not the same")
        self.assertEquals(actual_info['is_enabled'], expected_info['is_enabled'],
                          "The application enability status is not the same")

    def check_entity_save(self, response, test_data):
        """
        Checks whether the entity was saved successfully after POST, PUT or PATCH request. There are two checks.
        The first check will test whether expected fields are present in the output response or not. The second
        one will test whether expected fields are properly saved in the database or not.

        :param response: the response returned by the requests mentioned above
        :param test_data: a dictionary containing tested fields and their expected values.
        :return: nothing.
        """
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            self.check_detail_info(response.data, test_data)
            module = CorefacilityModuleSet().get(UUID(response.data['uuid']))
            self.assertTrue(module.is_application, "Only applications can be attached to the project")
            project_application_set = ProjectApplicationSet()
            project_application_set.project = self.project
            project_application_set.application = module
            project_application = None
            for set_item in project_application_set:
                self.assertIsNone(project_application, "The (project, application) pair must be unique")
                project_application = set_item
            self.assertEquals(project_application.is_enabled, test_data['is_enabled'],
                              "The link enability status must be correctly written to the database")


del BaseTestClass
