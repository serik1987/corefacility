from rest_framework import status
from parameterized import parameterized

from .base_test_class import BaseTestClass
from ..project_data_test_mixin_small import ProjectDataTestMixinSmall


class BaseProjectDataViewTest(ProjectDataTestMixinSmall, BaseTestClass):
    """
    Base class for testing all project-related views
    """

    @classmethod
    def setUpTestData(cls):
        """
        This method executes before all tests in the class and shall be used to create proper test environment
        for them
        """
        super().setUpTestData()
        cls.create_test_environment()

    @classmethod
    def tearDownClass(cls):
        """
        This method executes after all tests in the class and shall restore previous system state
        """
        cls.destroy_test_environment()
        super().tearDownClass()

    @parameterized.expand([
        ("default", "superuser", status.HTTP_201_CREATED),
        ("default", "full", status.HTTP_201_CREATED),
        ("default", "data_full", status.HTTP_201_CREATED),
        ("default", "data_add", status.HTTP_201_CREATED),
        ("default", "data_process", "data_process"),
        ("default", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_create(self, test_data_id, token_id, expected_status_code):
        """
        Tests creating action for entity views
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
        if isinstance(expected_status_code, str):
            expected_status_code = getattr(self, expected_status_code + "_status")
        self._test_entity_create(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("default", "superuser", status.HTTP_200_OK),
        ("default", "full", status.HTTP_200_OK),
        ("default", "data_full", status.HTTP_200_OK),
        ("default", "data_add", status.HTTP_200_OK),
        ("default", "data_process", status.HTTP_200_OK),
        ("default", "data_view", status.HTTP_200_OK),
        ("default", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_get(self, test_data_id, token_id, expected_status_code):
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
        if isinstance(expected_status_code, str):
            expected_status_code = getattr(self, expected_status_code + "_status")
        self._test_entity_get(test_data_id, token_id, expected_status_code)

    @parameterized.expand([
        ("default", "updated", "superuser", status.HTTP_200_OK),
        ("default", "updated", "full", status.HTTP_200_OK),
        ("default", "updated", "data_full", status.HTTP_200_OK),
        ("default", "updated", "data_add", status.HTTP_200_OK),
        ("default", "updated", "data_process", "data_process"),
        ("default", "updated", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "updated", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "updated", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", "updated", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_update(self, test_data_id, updated_data_id, token_id, expected_response_code):
        """
        Testing the update action for views.

        The data ID is a part of a public class field containing the data. To take the data this function
        will append the "_data" suffix to the data ID and will refer to the public field with a given name.

        The token ID is a part of a public class field containing the token. To take the token this function
        will append the "_token" suffix to the data ID and will refer to the public field with a given name
        :param test_data_id: ID for the initial data
        :param updated_data_id: ID for the data patch. PUTting the updated_data shall result in error 400 but
            PUTting the test_data + updated_data shall result in success
        :param token_id: token corresponding to the authorized user
        :param expected_response_code: the response code that you expect
        :return: nothing
        """
        if isinstance(expected_response_code, str):
            expected_response_code = getattr(self, expected_response_code + "_status")
        self._test_entity_update(test_data_id, updated_data_id, token_id, expected_response_code)

    @parameterized.expand([
        ("default", "updated", "superuser", status.HTTP_200_OK),
        ("default", "updated", "full", status.HTTP_200_OK),
        ("default", "updated", "data_full", status.HTTP_200_OK),
        ("default", "updated", "data_add", status.HTTP_200_OK),
        ("default", "updated", "data_process", "data_process"),
        ("default", "updated", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "updated", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "updated", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", "updated", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_entity_partial_update(self, test_data_id, updated_data_id, token_id, expected_response_code):
        """
        Testing the partial updating action for views.

        Testing the update action for views.

        The data ID is a part of a public class field containing the data. To take the data this function
        will append the "_data" suffix to the data ID and will refer to the public field with a given name.

        The token ID is a part of a public class field containing the token. To take the token this function
        will append the "_token" suffix to the data ID and will refer to the public field with a given name.

        :param test_data_id: ID for the initial data
        :param updated_data_id: ID for the data patch. PUTting the updated_data shall result in error 400 but
            PUTting the test_data + updated_data shall result in success.
        :param token_id: token corresponding to the authorized user.
        :param expected_response_code: the response code that you expect.
        :return: nothing
        """
        if isinstance(expected_response_code, str):
            expected_response_code = getattr(self, expected_response_code + "_status")
        self._test_entity_partial_update(test_data_id, updated_data_id, token_id, expected_response_code)

    @parameterized.expand([
        ("default", "superuser", status.HTTP_204_NO_CONTENT),
        ("default", "full", status.HTTP_204_NO_CONTENT),
        ("default", "data_full", status.HTTP_204_NO_CONTENT),
        ("default", "data_add", status.HTTP_403_FORBIDDEN),
        ("default", "data_process", status.HTTP_403_FORBIDDEN),
        ("default", "data_view", status.HTTP_403_FORBIDDEN),
        ("default", "no_access", status.HTTP_404_NOT_FOUND),
        ("default", "ordinary_user", status.HTTP_404_NOT_FOUND),
        ("default", None, status.HTTP_401_UNAUTHORIZED),
    ])
    def _test_entity_destroy(self, test_data_id, token_id, expected_status_code):
        """
        Tests the destroy action for views.

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


del BaseTestClass
