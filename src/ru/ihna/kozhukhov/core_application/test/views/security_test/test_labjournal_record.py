from rest_framework import status

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import Record, CategoryRecord

from .base_project_data_view_test import BaseProjectDataViewTest


class TestLabjournalRecord(BaseProjectDataViewTest):
    """
    Provides testing routines for the record inside a laboratory journal
    """

    default_data = {
        "type": "category",
        "alias": "adult",
    }
    """ Default data to create """

    data_process_status = status.HTTP_403_FORBIDDEN
    """ Status that must be returned if the user has 'data_process' access level """

    _tested_entity = Record
    """ The entity to test """

    @classmethod
    def attach_application(cls):
        """
        Does nothing because the labjournal records are part of the 'root' module.
        """
        pass

    def get_entity_list_path(self):
        """
        Returns path for the entity list requests (POST => creating new entity, GET => returns the entity list)

        :return: the entity list path
        """
        return "/api/{version}/projects/1/labjournal/categories/".format(version=self.API_VERSION)

    def check_detail_info(self, actual_info, expected_info):
        """
        Checks whether actual_info contains the same information that exists in the expected_info
        :param actual_info: the actual information
        :param expected_info: the expected information
        :return: nothing
        :except: assertion errors if condition fails
        """
        if isinstance(actual_info, dict):
            self.assertEquals(actual_info['type'], expected_info['type'], "Record type mismatch")
            self.assertEquals(actual_info['alias'], expected_info['alias'], "Category alias mismatch")
        elif isinstance(actual_info, CategoryRecord):
            self.assertEquals(actual_info.type.name, 'category', "Record type mismatch")
            self.assertEquals(actual_info.alias, expected_info['alias'], "Record alias mismatch")
        else:
            self.fail("Only categories should be created during the security tests.")


del BaseProjectDataViewTest
