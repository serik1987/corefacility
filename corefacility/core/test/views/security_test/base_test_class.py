from rest_framework import status

from core.entity.entity import Entity
from core.entity.entity_exceptions import EntityNotFoundException

from ..base_view_test import BaseViewTest


class BaseTestClass(BaseViewTest):
    """
    The base class for all view security tests.

    View security tests check whether proper user can correctly perform the CRUD operations
    and whether these operations are actually restricted.
    """

    _tested_entity = None
    """ Entity to test """

    alias_field = "alias"
    """ Alias field or None if not applicable """

    def _test_entity_create(self, test_data_id, token_id, expected_status_code):
        """
        Testing the create action for entity views.

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
        test_data = getattr(self, test_data_id + "_data")
        extra = self.get_authorization_headers(token_id)
        path = self.get_entity_list_path()
        response = self.client.post(path, data=test_data, format="json", **extra)
        self.assertEqual(response.status_code, expected_status_code)
        self.check_entity_save(response, test_data)
        self.check_4xx_details(response)

    def _test_entity_get(self, test_data_id, token_id, expected_status_code):
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
        test_data = getattr(self, test_data_id + "_data")
        entity_id = self.create_entity_for_test(test_data)
        id_lookup_path = self.get_entity_detail_path(entity_id)
        auth = self.get_authorization_headers(token_id)
        id_response = self.client.get(id_lookup_path, **auth)
        self.assertEquals(id_response.status_code, expected_status_code, "Unexpected status code for GET id response")
        if status.HTTP_200_OK <= id_response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            actual_id = id_response.data[self.id_field]
            self.assertEqual(actual_id, entity_id, "Entity IDs are not the same")
            self.check_detail_info(id_response.data, test_data)
        self.check_4xx_details(id_response)
        if self.alias_field is not None:
            alias = test_data[self.alias_field]
            alias_path = self.get_entity_detail_path(alias)
            alias_response = self.client.get(alias_path, **auth)
            self.assertEquals(alias_response.status_code, expected_status_code,
                              "Unexpected status code for GET alias response")
            if status.HTTP_200_OK <= alias_response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
                actual_id = alias_response.data[self.id_field]
                self.assertEqual(actual_id, entity_id, "Entity IDs are not the same")
                self.check_detail_info(alias_response.data, test_data)
            self.check_4xx_details(alias_response)

    def _test_entity_update(self, test_data_id, updated_data_id, token_id, expected_response_code):
        """
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
        test_data = getattr(self, test_data_id + "_data")
        updated_data = getattr(self, updated_data_id + "_data")
        entity_id = self.create_entity_for_test(test_data)
        path = self.get_entity_detail_path(entity_id)
        auth = self.get_authorization_headers(token_id)
        bad_response = self.client.put(path, data=updated_data, **auth)
        self.assertGreaterEqual(bad_response.status_code, status.HTTP_400_BAD_REQUEST,
                                "PUTting the updated_data alone shall result in error 400")
        full_data = test_data.copy()
        full_data.update(updated_data)
        good_response = self.client.put(path, data=full_data, **auth)
        self.assertEquals(good_response.status_code, expected_response_code, "PUTting")
        self.check_entity_save(good_response, full_data)
        self.check_4xx_details(good_response)

    def _test_entity_partial_update(self, test_data_id, updated_data_id, token_id, expected_response_code):
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
        test_data = getattr(self, test_data_id + "_data")
        updated_data = getattr(self, updated_data_id + "_data")
        entity_id = self.create_entity_for_test(test_data)
        entity_path = self.get_entity_detail_path(entity_id)
        auth = self.get_authorization_headers(token_id)
        response = self.client.patch(entity_path, updated_data, **auth)
        self.assertEquals(response.status_code, expected_response_code,
                          "The response code is not the same as expected")
        full_data = test_data.copy()
        full_data.update(updated_data)
        self.check_entity_save(response, full_data)
        self.check_4xx_details(response)

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
        test_data = getattr(self, test_data_id + "_data")
        entity_id = self.create_entity_for_test(test_data)
        entity_path = self.get_entity_detail_path(entity_id)
        auth = self.get_authorization_headers(token_id)
        response = self.client.delete(entity_path, **auth)
        self.assertEquals(response.status_code, expected_status_code, "Unexpected status code of the response")
        entity_set = self.get_tested_entity()._entity_set_class()
        if status.HTTP_200_OK <= response.status_code < status.HTTP_300_MULTIPLE_CHOICES:
            with self.assertRaises(EntityNotFoundException, msg="The entity has not been properly deleted"):
                entity_set.get(entity_id)
        self.check_4xx_details(response)

    def create_entity_for_test(self, test_data):
        """
        Creates the entity for testing purpose

        :param test_data: The data that shall be assigned to fields of the creating entity
        :return: ID of the newly created entity
        """
        entity_class = self.get_tested_entity()
        entity = entity_class(**test_data)
        entity.create()
        self.post_create_routines(entity)
        entity_id = getattr(entity, self.id_field)
        return entity_id

    def post_create_routines(self, entity):
        """
        This function will be called by _test_entity_get, _test_entity_put, _test_entity_patch immediately after
        the direct entity create

        :param entity: the entity that has been recently created.
        :return: useless
        """
        pass

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
            entity_set = self.get_tested_entity()._entity_set_class()
            actual_entity = entity_set.get(response.data[self.id_field])
            self.check_detail_info(actual_entity, test_data)

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info

        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        for key, expected_value in expected_info.items():
            actual_value = self.get_actual_value(actual_info, key)
            self.assertEquals(actual_value, expected_value,
                              "Necessary values were not stored correctly to the database during the object create")

    def check_4xx_details(self, response):
        """
        Tests whether 4xx-th response body has "detail" field. When False, assertion fails.

        :param response: the 4xx response
        :return: nothing
        """
        if response.status_code >= status.HTTP_401_UNAUTHORIZED:
            self.assertIn("detail", response.data)

    def get_actual_value(self, actual_info, key):
        """
        Returns the value from the actual_info

        :param actual_info: either the entity instance or part of the response body containing information about the
            single entity
        :param key: the tested field
        :return: value of the tested field
        """
        if isinstance(actual_info, Entity):
            actual_value = getattr(actual_info, key)
        else:
            actual_value = actual_info[key]
        return actual_value

    def get_tested_entity(self):
        """
        Returns the class of the tested entity

        :return: value of the '_tested_entity' public field
        :except: NotImplementedError if you don't re-implement the '_tested_entity' public field
        """
        if self._tested_entity is None:
            raise NotImplementedError("Please, define the 'tested_entity' public property")
        return self._tested_entity


del BaseViewTest
