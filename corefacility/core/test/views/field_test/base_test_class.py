from rest_framework import status

from ..base_view_test import BaseViewTest


class BaseTestClass(BaseViewTest):
    """
    This is the base class for all field validation tests.

    Field validation tests check each field by trying all valid and/or invalid values.
    """

    def _test_field_required(self, name, initial_data_id, is_required, is_present, default_value):
        """
        Checks whether the given field is required. The function tries to create the object leaving this field
        empty. If the field is required, there must be error 400. Otherwise, the entity must be successfully saved
        and retrieved.

        :param name: the field name
        :param initial_data_id: ID of the initial data. To receive the initial data the function adds "_data"
            suffix to the end of the initial data ID and looks for the class public field which name is the same
            as the resultant string
        :param is_required: True if the field is required. False otherwise
        :param is_present: True if the field shall present in the POST response as well as during the entity
            retrieve. False otherwise.
        :param default_value: The value that shall be assigned to the field. None for null | NULL
        :return: nothing
        """
        list_path = self.get_entity_list_path()
        initial_data = getattr(self, initial_data_id + "_data").copy()
        auth = {"HTTP_AUTHORIZATION": "Token " + self.superuser_token}
        response = self.client.post(list_path, data=initial_data, format="json", **auth)
        if is_required:
            self.check_field_invalidated(response, name)
        else:
            self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                              "The '{name}' field is not required".format(name=name))
            if is_present:
                self.check_field_validated(response, name, default_value)
            entity_id = response.data[self.id_field]
            detail_path = self.get_entity_detail_path(entity_id)
            output_response = self.client.get(detail_path, **auth)
            self.assertEquals(output_response.status_code, status.HTTP_200_OK, "The output response shall be OK")
            if is_present:
                self.check_field_validated(output_response, name, default_value)

    def _test_field_value(self, name, initial_data_id, initial_value, is_valid, is_present, expected_value):
        """
        Checks whether certain value to the field is valid. The test creates an object and checks the value
        containing in the POST response body. Next, it performs GET response and compares the field value.

        :param name: the field name
        :param initial_data_id: ID of the initial data. To receive the initial data the function adds "_data"
            suffix to the end of the initial data ID and looks for the class public field which name is the same
            as the resultant string. Also, the initial data shall contain all other fields except the considering one.
        :param initial_value: the initial value to assign during the object add
        :param is_valid: True if the value shall be valid, False otherwise
        :param is_present: True if the value shall be present in the response body, False otherwise
        :param expected_value: Expected value to be presented in the response body
        :return: nothing
        """
        input_path = self.get_entity_list_path()
        initial_data = getattr(self, initial_data_id + "_data").copy()
        initial_data[name] = initial_value
        auth = {"HTTP_AUTHORIZATION": "Token " + self.superuser_token}
        input_response = self.client.post(input_path, data=initial_data, format="json", **auth)
        if is_valid:
            self.assertEquals(input_response.status_code, status.HTTP_201_CREATED,
                              "The response status must be 201 CREATED for a field '{name}' filled correctly"
                              .format(name=name))
            if is_present:
                self.check_field_validated(input_response, name, expected_value)
                output_path = self.get_entity_detail_path(input_response.data[self.id_field])
                output_response = self.client.get(output_path, **auth)
                self.check_field_validated(output_response, name, expected_value)
        else:
            self.check_field_invalidated(input_response, name)

    def _test_read_only_field(self, name, initial_data_id, default_value):
        """
        Tests the read-only field.

        The read-only field can't be modified using a standard REST scheme. The client shall use some extra
        request to modify such a field

        :param name: the field name
        :param initial_data_id: ID of the initial data. To receive the initial data the function adds "_data"
            suffix to the end of the initial data ID and looks for the class public field which name is the same
            as the resultant string. Also, the initial data shall contain all other fields except the considering one.
        :param default_value: Value that shall be assigned to this field during the data create
        :return: nothing
        """
        input_path = self.get_entity_list_path()
        input_data = getattr(self, initial_data_id + "_data").copy()
        input_data[name] = "some-value"
        auth = self.get_superuser_authorization()
        response = self.client.post(input_path, data=input_data, **auth)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                          "The response must be successful even when you access to read-only fields")
        if default_value is not None:
            self.assertEquals(response.data[name], default_value,
                              "The read-only value '{name}' shall be unaffected by any request".format(name=name))
        entity_id = response.data[self.id_field]
        entity_path = self.get_entity_detail_path(entity_id)
        entity_response = self.client.get(entity_path, **auth)
        self.assertEquals(entity_response.status_code, status.HTTP_200_OK,
                          "The entity must be successfully read during this test")
        if default_value is not None:
            self.assertEquals(entity_response.data[name], default_value,
                              "The field must be unchanged during the data set")

    def check_field_invalidated(self, response, name):
        """
        Tests whether the field is not valid. If not, fails the test

        :param response: the response to be tested
        :param name: field name
        :return: nothing
        """
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST,
                          "Invalid value to the field '{name}' must give the 400th response".format(name=name))
        self.assertIn(name, response.data, "The 400th response to invalid field '{name}' must contain a response "
                                           "body in 'application/json' format where '{name}' field is mandatory"
                      .format(name=name))

    def check_field_validated(self, response, name, expected_value):
        """
        Checks whether particular field was transmitted correctly. If not, test fails.

        :param response: the response where the field shall be checked
        :param name: field name
        :param expected_value: expected field value
        :return: nothing.
        """
        self.assertIn(name, response.data, "The input field shall be presented in the response")
        self.assertEquals(response.data[name], expected_value,
                          "The input field value is not valid")

    def get_superuser_authorization(self):
        return {"HTTP_AUTHORIZATION": "Token " + self.superuser_token}


del BaseViewTest
