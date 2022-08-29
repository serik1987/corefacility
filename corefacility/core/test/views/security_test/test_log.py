from rest_framework import status
from rest_framework.test import APIClient
from parameterized import parameterized

from core.entity.log import Log, LogSet

from .base_log_test import BaseLogTest


def log_retrieve_provider():
    """
    Provides the data for the test_entity_retrieve function
    :return: list of arguments of that function
    """
    return [
        ("ordinary_user", 0, status.HTTP_403_FORBIDDEN),
        ("ordinary_user", "MAX+1", status.HTTP_403_FORBIDDEN),
        ("superuser", "MAX", status.HTTP_200_OK),
        (None, 0, status.HTTP_401_UNAUTHORIZED),
        ("superuser", "MAX+1", status.HTTP_404_NOT_FOUND),
        (None, "MAX+1", status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", "MAX", status.HTTP_403_FORBIDDEN),
        ("superuser", 0, status.HTTP_200_OK),
        (None, "MAX", status.HTTP_401_UNAUTHORIZED),
    ]


def log_modify_provider():
    """
    Provides the data for the test_entity_update, test_entity_destroy and test_entity_create routines
    :return: list of arguments of that function
    """
    return [
        ("ordinary_user", 0, status.HTTP_403_FORBIDDEN),
        ("ordinary_user", "MAX+1", status.HTTP_403_FORBIDDEN),
        ("superuser", "MAX", status.HTTP_405_METHOD_NOT_ALLOWED),
        (None, 0, status.HTTP_401_UNAUTHORIZED),
        ("superuser", "MAX+1", status.HTTP_405_METHOD_NOT_ALLOWED),
        (None, "MAX+1", status.HTTP_401_UNAUTHORIZED),
        ("ordinary_user", "MAX", status.HTTP_403_FORBIDDEN),
        ("superuser", 0, status.HTTP_405_METHOD_NOT_ALLOWED),
        (None, "MAX", status.HTTP_401_UNAUTHORIZED),
    ]


class TestLog(BaseLogTest):
    """
    Provides security tests for the logs and log lists
    """

    _tested_entity = Log
    """ Entity to test """

    _entity_set = LogSet()
    """ The entity set object to be used for checking the response results. The object must be initialized. """

    alias_field = None
    """ Alias field or None if not applicable """

    resource_name = "logs"
    """ The URL path segment between the '/api/{version}/' and '/{resource-id}/' parts. """

    log_create_data = {
        "log_address": "/path/to/file",
        "request_method": "post",
        "operation_description": "Sorry. The server was hacked.",
        "request_body": "This is our secret",
        "ip_address": "0.0.0.0",
        "user": None,
        "response_status": status.HTTP_200_OK,
        "response_body": "Everything we need.",
    }

    entity_id_list = None
    """ List of all entity IDs created during the setup """

    CREATE_USER_PATH = "/api/{version}/users/".format(version=BaseLogTest.API_VERSION)
    """ Path to create a single user """

    DELETE_USER_PATH = "/api/{version}/users/%d/".format(version=BaseLogTest.API_VERSION)
    """ Path to delete a single user """

    user_id = None
    """ ID of the lastly created user or None, if unapplicable """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_preconditions()
        cls.entity_id_list = []
        for entity in cls._entity_set:
            cls.entity_id_list.append(entity.id)

    @classmethod
    def create_test_preconditions(cls):
        """
        Creates all entities that are necessary for all tests to be completed successfully
        """
        cls.fill_sample_logs()
        cls.create_user({"HTTP_AUTHORIZATION": "Token " + cls.superuser_token})

    @classmethod
    def create_user(cls, auth_headers):
        """
        Sends some technical HTTP request that is used to create the user
        :param auth_headers: the authorization headers that shall be used to create the user
        :return: nothing
        """
        client = APIClient()
        response = client.post(cls.CREATE_USER_PATH, {"login": "sergei_kozhukhov"}, format="json",
                               **auth_headers)
        assert response.status_code == status.HTTP_201_CREATED
        cls.user_id = response.data['id']

    @parameterized.expand(log_modify_provider())
    def test_create_entity(self, token_id, entity_index, expected_status_code):
        """
        Tests whether anybody can create the entity
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param entity_index: index of the entity within the entity index list, "MAX" for the last entity in the list,
            "MAX+1" for some non-existent entity ID
        :param expected_status_code: status code to be expected
        :return: nothing
        """
        auth_headers = self.get_authorization_headers(token_id)
        entity_id = self.get_entity_id(entity_index)
        entity_data = self.get_create_data()
        response = self.client.post(self.get_entity_list_path(), entity_data, format="json", **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code")

    @parameterized.expand(log_retrieve_provider())
    def test_entity_retrieve(self, token_id, entity_index, expected_status_code):
        """
        Tests whether the entity can be retrieved correctly
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param entity_index: index of the entity within the entity index list, "MAX" for the last entity in the list,
            "MAX+1" for some non-existent entity ID
        :param expected_status_code: status code to be expected
        :return: nothing
        """
        auth_headers = self.get_authorization_headers(token_id)
        entity_id = self.get_entity_id(entity_index)
        response = self.retrieve_entity(entity_id, auth_headers, expected_status_code)
        if response.status_code == status.HTTP_200_OK:
            self.assert_entity_retrieved(response.data, self._entity_set.get(entity_id))

    @parameterized.expand(log_modify_provider())
    def test_entity_update(self, token_id, entity_index, expected_status_code):
        """
        Tests whether anybody can modify the entity
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param entity_index: index of the entity within the entity index list, "MAX" for the last entity in the list,
            "MAX+1" for some non-existent entity ID
        :param expected_status_code: status code to be expected
        :return: nothing
        """
        auth_headers = self.get_authorization_headers(token_id)
        entity_id = self.get_entity_id(entity_index)
        patch_data = self.get_patch_data(entity_id)
        response = self.client.patch(self.get_entity_detail_path(entity_id), patch_data, format="json",
                                     **auth_headers)
        self.assertEquals(response.status_code, expected_status_code,
                          "Unexpected status code during the entity update")

    @parameterized.expand(log_modify_provider())
    def test_entity_destroy(self, token_id, entity_index, expected_status_code):
        """
        Tests whether anybody can destroy the entity
        :param token_id: Authorization token is issued during the setUpTestData function and stored to "{id}_token"
            public field where {id} is token_id. User "superuser" for superuser authentication and "ordinary_user"
            for some unrelated ordinary user authentication. Also, use None for producing unauthenticated responses.
        :param entity_index: index of the entity within the entity index list, "MAX" for the last entity in the list,
            "MAX+1" for some non-existent entity ID
        :param expected_status_code: status code to be expected
        :return: nothing
        """
        auth_headers = self.get_authorization_headers(token_id)
        entity_id = self.get_entity_id(entity_index)
        response = self.client.delete(self.get_entity_detail_path(entity_id), **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code during the entity delete")

    def get_entity_id(self, entity_index):
        """
        Transforms the entity index used in the test functions to an entity ID
        :param entity_index: the entity index used in the test functions
        :return: the entity ID
        """
        if entity_index == "MAX+1":
            entity_id = max(self.entity_id_list) + 1
        elif entity_index == "MAX":
            entity_id = max(self.entity_id_list)
        else:
            entity_id = self.entity_id_list[entity_index]
        return entity_id

    def retrieve_entity(self, entity_id, auth_headers, expected_status_code):
        """
        Sends the HTTP request that retrieves a single entity
        :param entity_id: the entity ID
        :param auth_headers: authorization headers
        :param expected_status_code: status code to be expected. The test will be failed if actual response
            status code will not be the same as this value
        :return: the HTTP response
        """
        entity_detail_path = self.get_entity_detail_path(entity_id)
        response = self.client.get(entity_detail_path, **auth_headers)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected response status code")
        return response

    def get_patch_data(self, entity_id):
        """
        Returns the updating data for a given entity. Such data will be substituted to the PATCH request
        :param entity_id: the entity ID
        :return: the request data
        """
        return {"user": None, "ip_address": "127.0.0.1"}

    def get_create_data(self):
        """
        Defines the entity create data
        :return: nothing
        """
        return {
            "log_address": "/core",
            "request_method": "POST",
            "ip_address": "0.0.0.0",
            "request_body": "Sorry. Your server has been hacked."
        }

    def assert_entity_retrieved(self, actual_entity, expected_entity):
        """
        Asserts that the entity works properly
        :param actual_entity: data of the entity retrieve response
        :param expected_entity: the entity itself
        :return: nothing
        """
        self.assertEquals(actual_entity['id'], expected_entity.id, "Unexpected entity ID")
        self.assertEquals(str(actual_entity['request_date']), str(expected_entity.request_date.get()),
                          "Unexpected request date")
        self.assertEquals(str(actual_entity['log_address']), str(expected_entity.log_address),
                          "Unexpected log address")
        self.assertEquals(actual_entity['request_method'].lower(), expected_entity.request_method.lower(),
                          "Unexpected request method")
        self.assertEquals(actual_entity['operation_description'], expected_entity.operation_description,
                          "Unexpected operation description")
        self.assertEquals(actual_entity['request_body'], expected_entity.request_body, "Unexpected request body")
        self.assertEquals(actual_entity['input_data'], expected_entity.input_data, "Unexpected input data")
        self.assertEquals(actual_entity['user']['id'], expected_entity.user.id, "Unexpected user ID")
        self.assertEquals(actual_entity['user']['login'], expected_entity.user.login, "Unexpected user login")
        self.assertEquals(actual_entity['user']['name'], expected_entity.user.name, "Unexpected user name")
        self.assertEquals(actual_entity['user']['surname'], expected_entity.user.surname, "Unexpected user surname")
        self.assertEquals(str(actual_entity['ip_address']), str(expected_entity.ip_address), "Unexpected IP address")
        self.assertEquals(actual_entity['geolocation'], expected_entity.geolocation, "Unexpected geolocation info")
        self.assertEquals(actual_entity['response_status'], expected_entity.response_status,
                          "Unexpected response status")
        self.assertEquals(actual_entity['response_body'], expected_entity.response_body, "Unexpected response body")
        self.assertEquals(actual_entity['output_data'], expected_entity.output_data, "Unexpected output data")


del BaseLogTest
