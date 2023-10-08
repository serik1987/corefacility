from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from ...generic_views import EntityViewMixin


class TestFileSystem(APITestCase):
    """
    This is a base test class for testing user files providers and project files providers
    """

    LOGIN_PATH = "/api/v1/login/"

    ENTITY_LIST_PATH = None
    """ Path for downloading the entity list or creating new entity """

    ENTITY_DETAIL_PATH = None
    """ Path for entity read, modify or delete operations, Use %d placeholder to mark the entity ID """

    ENTITY_CREATE_DATA = None
    """ Data to be used for the entity create """

    ENTITY_UPDATE_DATA = None
    """ Data to be used for the entity update """

    auth_headers = None
    """ Headers that shall be placed for the authentication """

    entity_id = None
    """ ID of the lastly created entity or None if no entity has been created during the test """

    @classmethod
    def is_test_applicable(cls):
        """
        Defines conditions where all tests shall be run under
        :return: True if all tests shall be run, False if they shall be skipped
        """
        raise NotImplementedError("Please, define the is_test_applicable class method")

    @property
    def entity_list_path(self):
        """
        Path to deal with the entity list
        """
        if self.ENTITY_LIST_PATH is None:
            raise NotImplementedError("Please, define the ENTITY_LIST_PATH constant")
        return self.ENTITY_LIST_PATH

    @property
    def entity_detail_path(self):
        """
        Path to deal the single entities. The entity ID is marked by the '%d' placeholder
        """
        if self.ENTITY_DETAIL_PATH is None:
            raise NotImplementedError("Please, define the ENTITY_DETAIL_PATH constant")
        return self.ENTITY_DETAIL_PATH

    @property
    def entity_create_data(self):
        """
        Data that will be used for the entity create
        """
        if self.ENTITY_CREATE_DATA is None:
            raise NotImplementedError("Please, define the ENTITY_CREATE_DATA constant")
        return self.ENTITY_CREATE_DATA

    @property
    def entity_update_data(self):
        """
        Data to be used for the entity update
        """
        if self.ENTITY_UPDATE_DATA is None:
            raise NotImplementedError("Please, define the ENTITY_UPDATE_DATA constant")
        return self.ENTITY_UPDATE_DATA

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        EntityViewMixin.throttle_classes = []
        if cls.is_test_applicable():
            client = APIClient()
            result = client.post(cls.LOGIN_PATH)
            assert result.status_code == status.HTTP_200_OK
            token = result.data['token']
            cls.auth_headers = {"HTTP_AUTHORIZATION": "Token " + token}

    @classmethod
    def tearDownClass(cls):
        if hasattr(EntityViewMixin, "throttle_classes"):
            del EntityViewMixin.throttle_classes
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.entity_id = None
        if not self.is_test_applicable():
            self.skipTest("The test is not applicable under given server configuration")

    def test_entity_create_and_delete(self):
        """
        Tests whether the directory is automatically created during the entity create.
        """
        entity_data = self.create_entity()
        self.assert_entity_dir_created(entity_data)
        self.create_test_file(entity_data)
        self.delete_entity()
        self.assert_entity_dir_deleted(entity_data)

    def test_entity_update(self):
        """
        Tests whether the entity can be successfully updated
        """
        original_data = self.create_entity()
        self.create_test_file(original_data)
        updated_data = self.update_entity()
        self.assert_entity_dir_deleted(original_data)
        self.assert_entity_dir_created(updated_data)
        self.assert_test_file_exists(updated_data)
        self.delete_entity()
        self.assert_entity_dir_deleted(updated_data)

    def create_entity(self):
        """
        Creates an entity and put the entity ID to the entity_id public property.
        :return: the data corresponding to the entity
        """
        response = self.client.post(self.entity_list_path, self.entity_create_data, format="json", **self.auth_headers)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                          "Unable to create entity: unexpected response status")
        self.entity_id = response.data['id']
        return response.data

    def update_entity(self):
        """
        Updates the entity using the PATCH request
        :return: the data corresponding to the updated entity
        """
        entity_update_path = self.entity_detail_path % self.entity_id
        result = self.client.patch(entity_update_path, self.entity_update_data, format="json", **self.auth_headers)
        self.assertEquals(result.status_code, status.HTTP_200_OK,
                          "Unable to update the entity: unexpected status code")
        self.entity_id = result.data['id']
        return result.data

    def delete_entity(self):
        """
        Deletes the lastly created entity
        :return: nothing
        """
        if self.entity_id is None:
            raise RuntimeError("The entity is expected to be created during this test")
        entity_delete_path = self.entity_detail_path % self.entity_id
        response = self.client.delete(entity_delete_path, **self.auth_headers)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT,
                          "Unable to delete entity: unexpected response status")
        self.entity_id = None

    def assert_entity_dir_created(self, entity_data):
        """
        Asserts that the home directory for the entity has been created
        :param entity_data: the entity data returned by the create_entity function
        :return: nothing
        """
        raise NotImplementedError("assert_entity_dir_created")

    def create_test_file(self, entity_data):
        """
        Creates test file in the entity directory
        :param entity_data: the entity data returned by the create_entity function
        :return: nothing
        """
        raise NotImplementedError("create_test_file")

    def assert_test_file_exists(self, entity_data):
        """
        Asserts that the test file still exists in the entity directory
        :param entity_data: the entity data returned during the last create/update request
        :return: nothing
        """
        raise NotImplementedError("assert_test_file_exists')")

    def assert_entity_dir_deleted(self, entity_data):
        """
        Asserts that the home directory for the entity has been deleted
        :param entity_data: the entity data returned by the delete_entity function
        :return: nothing
        """
        raise NotImplementedError("assert_entity_dir_deleted")
