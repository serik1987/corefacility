from rest_framework import status
from parameterized import parameterized

from core.entity.user import UserSet
from core.entity.group import Group
from core.entity.project import Project

from .base_test_class import BaseTestClass


def standard_security_test_provider(status_ok, status_error):
    """
    Provides the project test data for the security tests

    :param status_ok: expected status code when the request is allowed
    :param status_error: expected status code when the request is prohibited
    :return: list of possible arguments for test_project_get function
    """
    return [
        ("superuser", "superuser", status_ok),
        ("superuser", "ordinary_user", status_error),
        ("ordinary_user", "superuser", status_ok),
        ("ordinary_user", "ordinary_user", status_ok),
    ]


def project_add_provider():
    """
    Provides the test data for the project add feature.

    :return: Arguments for the test_project_data function
    """
    return [
        ("superuser", "new_project_new_group", None, status.HTTP_201_CREATED),
        ("superuser", "new_project_current_group", "superuser", status.HTTP_201_CREATED),
        ("superuser", "new_project_current_group", "ordinary_user", status.HTTP_400_BAD_REQUEST),
        ("ordinary_user", "new_project_new_group", None, status.HTTP_201_CREATED),
        ("ordinary_user", "new_project_current_group", "superuser", status.HTTP_400_BAD_REQUEST),
        ("ordinary_user", "new_project_current_group", "ordinary_user", status.HTTP_201_CREATED),
        (None, "new_project_new_group", None, status.HTTP_401_UNAUTHORIZED),
        (None, "new_project_current_group", "ordinary_user", status.HTTP_401_UNAUTHORIZED),
    ]


class TestProject(BaseTestClass):
    """
    Provides testing for project create, retrieve, update, partial_update and delete actions (w/o security tests)
    """

    _tested_entity = Project
    resource_name = "projects"
    ordinary_user_required = True

    superuser_id = None
    ordinary_user_id = None

    superuser_group_id = None
    ordinary_user_group_id = None

    superuser_project_data = {
        "alias": "superuser",
        "name": "The Superuser Project",
        "root_group": None
    }

    ordinary_user_project_data = {
        "alias": "ordinary_user",
        "name": "The Ordinary User Project",
        "root_group": None
    }
    project_update_data = {
        "name": "New Project Name",
    }

    new_project_new_group_data = {
        "name": "The New Project",
        "alias": "new",
        "root_group_id": None,
        "root_group_name": "The New Group",
    }

    new_project_current_group_data = {
        "name": "The New Project",
        "alias": "new",
        "root_group_id": None,
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.get_user_and_group_id("superuser", "superuser")
        cls.get_user_and_group_id("ordinary_user", "user")

    @classmethod
    def get_user_and_group_id(cls, field_name, login):
        user = UserSet().get(login)
        setattr(cls, field_name + "_id", user.id)
        group = Group(name="The %s Group" % login.capitalize(), governor=user)
        group.create()
        setattr(cls, field_name + "_group_id", group.id)
        project_data = getattr(cls, field_name + "_project_data")
        project_data["root_group"] = group

    @parameterized.expand(standard_security_test_provider(status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))
    def test_project_get(self, test_data_id, token_id, expected_status_code):
        """
        Testing the get action for entity views.

        :param test_data_id: The test data contains in the public field "{id}_data" where {id} is test_data_id
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param expected_status_code: a status code that shall be checked. If status code is between 200 and 299
            an additional check for the response body is provided
        :return: nothing
        :except: assertion error if status code is not the same as expected_status_code or test data were either
            not saved correctly or not contained in the response body
        """
        self._test_entity_get(test_data_id + "_project", token_id, expected_status_code)

    @parameterized.expand(standard_security_test_provider(status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))
    def test_project_update(self, test_data_id, token_id, expected_status_code):
        """
        Testing the get action for entity views.

        :param test_data_id: The test data contains in the public field "{id}_data" where {id} is test_data_id
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param expected_status_code: a status code that shall be checked. If status code is between 200 and 299
            an additional check for the response body is provided
        :return: nothing
        :except: assertion error if status code is not the same as expected_status_code or test data were either
            not saved correctly or not contained in the response body
        """
        self._test_entity_update(test_data_id + "_project", "project_update", token_id, expected_status_code)

    @parameterized.expand(standard_security_test_provider(status.HTTP_200_OK, status.HTTP_404_NOT_FOUND))
    def test_entity_partial_update(self, test_data_id, token_id, expected_response_code):
        """
        Testing the partial updating action for views.

        Testing the update action for views.

        The data ID is a part of a public class field containing the data. To take the data this function
        will append the "_data" suffix to the data ID and will refer to the public field with a given name.

        The token ID is a part of a public class field containing the token. To take the token this function
        will append the "_token" suffix to the data ID and will refer to the public field with a given name.

        :param test_data_id: ID for the initial data
        :param token_id: token corresponding to the authorized user.
        :param expected_response_code: the response code that you expect.
        :return: nothing
        """
        self._test_entity_partial_update(test_data_id + "_project", "project_update", token_id, expected_response_code)

    @parameterized.expand(project_add_provider())
    def test_project_add(self, token_id, project_data, root_group_id, expected_status_code):
        """
        Tests the project add feature

        :param token_id: ID for the user token
        :param project_data: 'new_project_new_group' will test project creation together with new group creation,
            'new_project_current_group' will test project creation and its attachment to one of the pre-existent groups
        :param root_group_id: 'superuser' will use "The Superuser Group", 'ordinary_user' will user "The User Group"
            Such parameter is ignored when 'project_data' is 'new_project_new_group'
        :param expected_status_code: the response status code expected by the tester.
        :return: nothing
        """
        if project_data == "new_project_current_group":
            root_group_id = getattr(self, root_group_id + "_group_id")
            self.new_project_current_group_data["root_group_id"] = root_group_id
        self._test_entity_create(project_data, token_id, expected_status_code)

    @parameterized.expand(standard_security_test_provider(status.HTTP_204_NO_CONTENT, status.HTTP_404_NOT_FOUND))
    def test_project_destroy(self, project_data, token_id, expected_status_code):
        """
        Tests whether the project can be properly destroyed

        :param project_data: ID for the project data
        :param token_id: ID for the authorization token
        :param expected_status_code: response status code expected by the tester
        :return: nothing
        """
        self._test_entity_destroy(project_data + "_project", token_id, expected_status_code)

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info

        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        self.assertEquals(self.get_actual_value(actual_info, "alias"), expected_info["alias"],
                          "Project aliases must be the same")
        self.assertEquals(self.get_actual_value(actual_info, "name"), expected_info["name"],
                          "Project names must be the same")
        actual_root_group = self.get_actual_value(actual_info, "root_group")
        if "root_group" in expected_info:
            expected_root_group = expected_info["root_group"]
            self.assertEquals(self.get_actual_value(actual_root_group, "id"),
                              self.get_actual_value(expected_root_group, "id"),
                              "Root group IDs must be the same")
            self.assertEquals(self.get_actual_value(actual_root_group, "name"),
                              self.get_actual_value(expected_root_group, "name"),
                              "Root group names are not the same")


del BaseTestClass
