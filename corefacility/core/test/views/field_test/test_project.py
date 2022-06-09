from rest_framework import status
from parameterized import parameterized

from core.entity.group import Group, GroupSet
from core.entity.user import UserSet

from .base_test_class import BaseTestClass
from .data_providers import slug_provider, arbitrary_string_provider


def root_group_post_provider():
    return [
        #   root_group_id root_group_name is_valid    group_shall_be_created  group_id    group_name
        (   -1,           -1,             False,      None,                   None,       None),
        (   -1,           None,           False,      None,                   None,       None),
        (   None,         -1,             False,      None,                   None,       None),
        (   None,         None,           False,      None,                   None,       None),
        (   None,         "Some group",   True,       True,                   False,      "Some group"),
        (   0,            -1,             True,       False,                  True,       "The Default Group"),
        (   0,            "Some group",   True,       False,                  True,       "The Default Group"),
    ]


def root_group_modify_provider():
    preliminary_data = [
        #   root_group_id root_group_name is_valid    group_shall_be_created  group_id    group_name
        (   -1,           -1,             True,       False,                  -1,         "Вазомоторные колебания"),
        (   None,         -1,             False,      None,                   None,       None),
        (   None,         None,           False,      None,                   None,       None),
        (   None,         "Some group",   True,       True,                   0,          "Some group"),
        (   0,            -1,             True,       False,                  1,          "The Default Group"),
        (   0,            "Some group",   True,       False,                  1,          "The Default Group"),
    ]
    return [(method_name, *other_args) for method_name in ("patch", "put") for other_args in preliminary_data]


class TestProject(BaseTestClass):
    """
    Provides field validation tests for single projects
    """

    resource_name = "projects"

    default_group = None

    no_alias_data = {
        "name": "Some project",
        "root_group_id": None,
        "root_group_name": "Some project group"
    }

    no_name_data = {
        "alias": "some-project",
        "root_group_id": None,
        "root_group_name": "Some project group",
    }

    no_root_group_data = {
        "alias": "vasomotor-oscillations",
        "name": "Вазомоторные колебания",
    }

    new_root_group_data = {
        "alias": "vasomotor-oscillations",
        "name": "Вазомоторные колебания",
        "root_group_id": None,
        "root_group_name": "Вазомоторные колебания",
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_group = Group(name="The Default Group", governor=UserSet().get("superuser"))
        cls.default_group.create()

    @parameterized.expand(slug_provider(64))
    def test_alias_valid(self, alias_value, is_valid):
        """
        Checks the project alias validation feature

        :param alias_value: tested value
        :param is_valid: True is such an alias is valid, False otherwise
        :return: nothing
        """
        self._test_field_value("alias", "no_alias", alias_value, is_valid, True, alias_value)

    def test_alias_required(self):
        """
        Checks whether the alias field is treated as required

        :return: nothing
        """
        self._test_field_required("alias", "no_alias", True, True, None)

    def test_alias_duplicated(self):
        """
        Checks whether the client can create two projects with the same alias

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        path = self.get_entity_list_path()
        first_project_response = self.client.post(path, data=self.new_root_group_data, format="json", **headers)
        self.assertEquals(first_project_response.status_code, status.HTTP_201_CREATED,
                          "The first project creation must be successful")
        another_data = self.no_alias_data.copy()
        another_data['alias'] = self.new_root_group_data['alias']
        second_project_response = self.client.post(path, data=another_data, format="json", **headers)
        self.check_response_duplication_error(second_project_response)

    def test_alias_duplicated_change(self):
        """
        Checks whether the alias can be changed to the duplicated value

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        path = self.get_entity_list_path()
        first_project_create_response = self.client.post(path, data=self.new_root_group_data, format="json", **headers)
        self.assertEquals(first_project_create_response.status_code, status.HTTP_201_CREATED,
                          "The first project creation must be successful during this test")
        another_data = self.no_alias_data.copy()
        another_data['alias'] = 'another-alias'
        second_project_create_response = self.client.post(path, data=another_data, format="json", **headers)
        self.assertEquals(second_project_create_response.status_code, status.HTTP_201_CREATED)
        alias_modification_path = self.get_entity_detail_path(second_project_create_response.data['id'])
        alias_modification_response = self.client.patch(alias_modification_path,
                                                        data={"alias": "vasomotor-oscillations"},
                                                        format="json",
                                                        **headers)
        self.check_response_duplication_error(alias_modification_response)

    @parameterized.expand(arbitrary_string_provider(False, 64))
    def test_name_value(self, value, is_valid):
        """
        checks the server-side validation for the project name field

        :param value: tested value for the project name
        :param is_valid: True if such a value is expected to be valid, False if the value is expected to be invalid
        :return: nothing
        """
        self._test_field_value("name", "no_name", value, is_valid, True, value)

    def test_name_required(self):
        """
        Checks whether the project name is required field

        :return: nothing
        """
        self._test_field_required("name", "no_name", True, True, None)

    def test_name_duplicated(self):
        """
        Tests whether the client may create two projects with the same name

        :return: nothing
        """
        path = self.get_entity_list_path()
        headers = self.get_authorization_headers("superuser")
        create_first_project_response = self.client.post(path, data=self.new_root_group_data, format="json",
                                                         **headers)
        self.assertEquals(create_first_project_response.status_code, status.HTTP_201_CREATED,
                          "The first project shall be successfully created")
        another_project_data = self.no_name_data.copy()
        another_project_data["name"] = create_first_project_response.data["name"]
        create_second_project_response = self.client.post(path, data=another_project_data, format="json",
                                                          **headers)
        self.check_response_duplication_error(create_second_project_response)

    def test_name_duplicated_change(self):
        """
        Checks whether the client may change the name of the project to the existent one

        :return: nothing
        """
        create_path = self.get_entity_list_path()
        headers = self.get_authorization_headers("superuser")
        create_first_project_response = self.client.post(create_path, data=self.new_root_group_data, format="json",
                                                         **headers)
        self.assertEquals(create_first_project_response.status_code, status.HTTP_201_CREATED,
                          "The first project shall be created successfully during this test")
        second_project_data = self.no_name_data.copy()
        second_project_data['name'] = "Some project name"
        create_second_project_response = self.client.post(create_path, data=second_project_data, format="json",
                                                          **headers)
        self.assertEquals(create_second_project_response.status_code, status.HTTP_201_CREATED,
                          "The second project shall be created successfully during this test")
        project_modification_path = self.get_entity_detail_path(create_second_project_response.data['id'])
        project_modification_data = {"name": create_first_project_response.data["name"]}
        project_modification_response = self.client.patch(project_modification_path,
                                                          data=project_modification_data, format="json", **headers)
        self.check_response_duplication_error(project_modification_response)

    @parameterized.expand(arbitrary_string_provider(True, 1024))
    def test_description_value(self, value, is_valid):
        """
        Checks the project description validation feature at the server side

        :param value:value of the project description
        :param is_valid: True if this value is expected to be valid, False is the value is expected to be invalid
        :return: nothing
        """
        self._test_field_value("description", "new_root_group", value, is_valid, True, value)

    def test_description_required(self):
        """
        Checks whether the description field is required

        :return: nothing
        """
        self._test_field_required("description", "new_root_group", False, True, None)

    @parameterized.expand([
        ("governor", ("id", "login", "name", "surname")),
        ("root_group", ("id", "name")),
    ])
    def test_read_only_object_fields(self, field_name, child_field_names):
        input_path = self.get_entity_list_path()
        headers = self.get_superuser_authorization()
        creation_result = self.client.post(input_path, data=self.new_root_group_data, format="json",
                                           **headers)
        self.assertEquals(creation_result.status_code, status.HTTP_201_CREATED,
                          "The project must be successfully created")
        detail_path = self.get_entity_detail_path(creation_result.data['id'])
        modification_result = self.client.patch(detail_path, data={field_name: "some value"}, format="json",
                                                **headers)
        self.assertEquals(modification_result.status_code, status.HTTP_200_OK,
                          "The project must be successfully modified at this test")
        for child_field_name in child_field_names:
            self.assertEquals(modification_result.data[field_name][child_field_name],
                              creation_result.data[field_name][child_field_name],
                              "The read-only field has been suddenly changed")

    @parameterized.expand(root_group_post_provider())
    def test_root_group_post(self, root_group_id, root_group_name, is_valid, group_shall_be_created,
                             desired_group_id, desired_group_name):
        """
        Tests the 'root_group_id' and 'root_group_name' fields on the group create

        :param root_group_id: value of the 'root_group_id' parameter or -1 if such parameter shall be omitted or
            0 if such parameter shall be ID of the 'The Default Group'
        :param root_group_name: value of the 'root_group_name' parameter or -1 if such parameter shall be omitted
        :param is_valid: True if such combination of parameters is valid, False if the combination is invalid
        :param group_shall_be_created: True if new group is expected to be created, False otherwise
        :param desired_group_id: True if group ID is the same as the ID of the group 'The Default Group'
            False if group ID check shall be ignored
        :param desired_group_name: The output group name
        :return: nothing
        """
        group_set = GroupSet()
        original_length = len(group_set)
        path = self.get_entity_list_path()
        project_data = self.no_root_group_data.copy()
        self.update_root_group_id_and_name(project_data, root_group_id, root_group_name)
        headers = self.get_superuser_authorization()
        response = self.client.post(path, data=project_data, format="json", **headers)
        if is_valid:
            self.assertEquals(response.status_code, status.HTTP_201_CREATED,
                              "The project create must be OK for such combination of root group options")
            final_length = len(group_set)
            if group_shall_be_created:
                self.assertEquals(final_length, original_length+1,
                                  "Such combination of 'root_group_id' and 'root_group_name' parameters imply "
                                  "that new group shall be created")
            else:
                self.assertEquals(final_length, original_length,
                                  "Such combination of 'root_group_id' and 'root_group_name' parameters imply "
                                  "that no new groups shall be created")
            if desired_group_id:
                self.assertEquals(response.data['root_group']['id'], self.default_group.id,
                                  "The combination of parameters imply attachment of the project "
                                  "to the 'The Default Group'")
            actual_root_group = self.check_root_group_and_governor(response)
            self.assertEquals(actual_root_group.name, desired_group_name, "Undesirable group name")
        else:
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST,
                              "The project create shall be failed for such combination of root group options")

    @parameterized.expand(root_group_modify_provider())
    def test_root_group_modify(self, method_name, root_group_id, root_group_name, is_valid, group_shall_be_created,
                               desired_group_id, desired_group_name):
        """
        Tests the modification of the group ID and group name

        :param method_name: either 'put' for PUT request or 'patch' for PATCH request
        :param root_group_id: value of the 'root_group_id' parameter or -1 if such parameter shall be omitted or
            0 if such parameter shall be ID of the 'The Default Group'
        :param root_group_name: value of the 'root_group_name' parameter or -1 if such parameter shall be omitted
        :param is_valid: True if such combination of parameters is valid, False if the combination is invalid
        :param group_shall_be_created: True if new group is expected to be created, False otherwise
        :param desired_group_id: 1 if the project shall be attached for the group 'The Desired Group',
            0 if the project shall be attached to the newly created group,
            -1 if group attachment shall not be changed
        :param desired_group_name: The output group name
        :return: nothing
        """
        group_set = GroupSet()
        project_create_path = self.get_entity_list_path()
        project_data = self.new_root_group_data.copy()
        headers = self.get_superuser_authorization()
        project_create_response = self.client.post(project_create_path, data=project_data, format="json", **headers)
        original_group_number = len(group_set)
        self.assertEquals(project_create_response.status_code, status.HTTP_201_CREATED,
                          "The project must be created successfully at this test")
        request_function = getattr(self.client, method_name)
        project_modification_path = self.get_entity_detail_path(project_create_response.data['id'])
        del project_data["root_group_id"]
        del project_data["root_group_name"]
        self.update_root_group_id_and_name(project_data, root_group_id, root_group_name)
        project_modification_response = request_function(project_modification_path, data=project_data, format="json",
                                                         **headers)
        if is_valid:
            self.assertEquals(project_modification_response.status_code, status.HTTP_200_OK,
                              "The project shall be successfully modified")
            final_group_number = len(group_set)
            if group_shall_be_created:
                self.assertEquals(final_group_number, original_group_number+1, "New group shall be created")
            else:
                self.assertEquals(final_group_number, original_group_number, "New group shall not be created")
            actual_root_group = self.check_root_group_and_governor(project_modification_response)
            if desired_group_id == 1:
                self.assertEquals(actual_root_group.id, self.default_group.id,
                                  "The project root group shall be changed to the 'root_group' value")
            elif desired_group_id == -1:
                self.assertEquals(actual_root_group.id, project_create_response.data['root_group']['id'],
                                  "The project 'root_group' shall be leaved unmodified")
            self.assertEquals(actual_root_group.name, desired_group_name,
                              "Unexpected root group name")
        else:
            self.assertEquals(project_modification_response.status_code, status.HTTP_400_BAD_REQUEST,
                              "This couple of data is considered to be invalid")

    @parameterized.expand([("project_dir",), ("unix_group",)])
    def test_all_read_only_fields(self, field_name):
        self._test_read_only_field(field_name, "new_root_group", None)

    def check_response_duplication_error(self, response):
        """
        Checks whether the response notifies the client that duplication error was occured at the server side

        :param response: the response to be explored
        :return: nothing
        """
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST,
                          "The response can't be modified to the existent one")
        self.assertEquals(response.data['code'], "EntityDuplicatedException",
                          "The response body must contain the 'code' field with 'EntityDuplicatedException' value")

    def update_root_group_id_and_name(self, project_data, root_group_id, root_group_name):
        """
        Puts the 'root_group_id' and 'root_group_name' fields to the request body

        :param project_data: the request body
        :param root_group_id: value of the 'root_group_id' parameter or -1 if such parameter shall be omitted or
            0 if such parameter shall be ID of the 'The Default Group'
        :param root_group_name: value of the 'root_group_name' parameter or -1 if such parameter shall be omitted
        :return:
        """
        if root_group_id == 0:
            root_group_id = self.default_group.id
        if root_group_id != -1:
            project_data['root_group_id'] = root_group_id
        if root_group_name != -1:
            project_data['root_group_name'] = root_group_name

    def check_root_group_and_governor(self, response):
        """
        Checks the validity of the root group and the governor

        :param response: the response received from the POST, PATCH or PUT request
        :return: the root group for a particular project (instance of the core.entity.group.Group class)
        """
        root_group_id = response.data['root_group']['id']
        root_group = GroupSet().get(root_group_id)
        self.assertEquals(response.data['root_group']['name'], root_group.name,
                          "Root group name inconsistency")
        self.assertEquals(response.data['governor']['id'], root_group.governor.id,
                          "Governor ID inconsistency")
        self.assertEquals(response.data['governor']['login'], root_group.governor.login,
                          "Governor login inconsistency")
        self.assertEquals(response.data['governor']['name'], root_group.governor.name,
                          "Governor name inconsistency")
        self.assertEquals(response.data['governor']['surname'], root_group.governor.surname,
                          "Governor surname inconsistency")
        return root_group


del BaseTestClass
