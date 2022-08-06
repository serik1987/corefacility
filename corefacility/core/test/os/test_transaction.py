from django.conf import settings
from rest_framework import status

from core.entity.user import User, UserSet
from core.entity.group import GroupSet
from core.entity.log import LogSet
from core.entity.log_record import LogRecordSet
from core.entity.entity_exceptions import EntityNotFoundException
from core.transaction import CorefacilityTransaction
from core.os import CommandMaker

from ..views.base_view_test import BaseViewTest


class TestTransaction(BaseViewTest):
    """
    Tests the corefacility transaction processes.

    The transaction processes are such processes that will be completed in 'all-or-none' principle.

    This means that the process is either completed or all system remains to be intact.
    """

    superuser_required = True
    ordinary_user_required = True

    def test_settings_ok(self):
        """
        Tests whether the settings that define the interaction of the server application with the operating system
        are correctly adjusted

        :return: nothing
        """
        if settings.CORE_UNIX_ADMINISTRATION and settings.CORE_SUGGEST_ADMINISTRATION:
            self.fail("The CORE_UNIX_ADMINISTRATION and CORE_SUGGEST_ADMINISTRATION settings "
                      "can't be True simultaneously")

    def test_transaction_success(self):
        """
        Tests whether the transaction can be returned successfully

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.post(self.get_test_request_path("."), **headers)
        log = self.check_log_existence()
        if settings.CORE_UNIX_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            self.assert_log_record(log)
        if settings.CORE_SUGGEST_ADMINISTRATION:
            self.assert_suggestion(response, ("ls -l .",))
            self.check_group_existence(False, False)
            self.check_no_log_records(log)
        if not settings.CORE_UNIX_ADMINISTRATION and not settings.CORE_SUGGEST_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            self.check_no_log_records(log)

    def test_transaction_failure(self):
        """
        Tests what can be happened if transaction will be failed to be executed

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.post(self.get_test_request_path("some-nonexistent-dir"), **headers)
        log = self.check_log_existence()
        if settings.CORE_UNIX_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, "Unexpected status code")
            self.assertEquals(response.data['code'], "posix_error", "Unexpected response body")
            self.check_group_existence(False, False)
            self.assert_log_record(log, level="ERR")
        if settings.CORE_SUGGEST_ADMINISTRATION:
            self.assert_suggestion(response, ("ls -l some-nonexistent-dir",))
            self.check_group_existence(False, False)
            self.check_no_log_records(log)
        if not settings.CORE_UNIX_ADMINISTRATION and not settings.CORE_SUGGEST_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            self.check_no_log_records(log)

    def test_transaction_safe_mode(self):
        """
        Tests whether transaction can be successful in the test mode

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.get(self.get_test_request_path("."), **headers)
        log = None
        if settings.DEBUG:
            log = self.check_log_existence()
        else:
            self.check_no_log()
        if settings.CORE_UNIX_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            if log:
                self.assert_log_record(log)
        if settings.CORE_SUGGEST_ADMINISTRATION:
            self.assert_suggestion(response, ("ls -l .",))
            self.check_group_existence(False, False)
            self.check_no_log_records(log)
        if not settings.CORE_UNIX_ADMINISTRATION and not settings.CORE_SUGGEST_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            if log:
                self.check_no_log_records(log)

    def test_commands_with_no_transaction(self):
        """
        Tests whether commands can be run without any transaction

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.put(self.get_test_request_path("."), **headers)
        log = self.check_log_existence()
        if settings.CORE_UNIX_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            self.check_no_log_records(log)
        if settings.CORE_SUGGEST_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            self.check_no_log_records(log)
        if not settings.CORE_UNIX_ADMINISTRATION and not settings.CORE_SUGGEST_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, False)
            self.check_no_log_records(log)

    def test_closed_transaction(self):
        """
        Tests the possibility for the enclosed transaction (that is, transaction inside another transaction)

        :return: nothing
        """
        headers = self.get_authorization_headers("superuser")
        response = self.client.patch(self.get_test_request_path("."), **headers)
        log = self.check_log_existence()
        if settings.CORE_UNIX_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, True)
            self.check_two_log_records(log)
        if settings.CORE_SUGGEST_ADMINISTRATION:
            self.assert_suggestion(response, ("ls -l .", "ls -l /var/log"))
            self.check_group_existence(False, False)
            self.check_no_log_records(log)
        if not settings.CORE_UNIX_ADMINISTRATION and not settings.CORE_SUGGEST_ADMINISTRATION:
            self.assertEquals(response.status_code, status.HTTP_200_OK, "Unexpected status code")
            self.check_group_existence(True, True)
            self.check_no_log_records(log)

    def test_security(self):
        """
        Tests whether ordinary user can execute the test request

        :return: nothing
        """
        headers = self.get_authorization_headers("ordinary_user")
        response = self.client.post(self.get_test_request_path("."), **headers)
        log = self.check_log_existence()
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)
        self.check_group_existence(False, False)
        self.check_no_log_records(log)

    def test_another_failure(self):
        """
        Tests whether transaction will be completed in case of internal errors

        :return: nothing
        """
        CommandMaker().initialize_executor(self)
        with self.assertRaises(NameError):
            with CorefacilityTransaction():
                user = User(login="sergei.kozhukhov", name="Sergei", surname="Kozhukhov")
                user.create()
                raise NameError("Some sample error")
        with self.assertRaises(EntityNotFoundException,
                               msg="The transaction has not been aborted when exception occured"):
            UserSet().get("sergei.kozhukhov")
        CommandMaker().clear_executor(self)

    def get_test_request_path(self, test_value):
        """
        Gets the test request path

        :param test_value: a sample command line argument
        :return: the test requre
        """
        return "/api/{version}/__test__/transaction/{dirname}/".format(
            version=self.API_VERSION,
            dirname=test_value
        )

    def check_group_existence(self, some_group, other_group):
        """
        Checks whether the group has been actually written to the database

        :param some_group: Checks whether 'The Some Group' has been written
        :param other_group: Checks whether 'The Other Group' has been written
        :return: nothing
        """
        actual_some_group = False
        actual_other_group = False
        for group in GroupSet():
            if group.name == "The Some Group":
                actual_some_group = True
            if group.name == "The Other Group":
                actual_other_group = True
        self.assertEquals(actual_some_group, some_group, "Error in writing 'The Some Group': data inconsistency")
        self.assertEquals(actual_other_group, other_group, "Error in writing 'The Other Group': data inconsistency")

    def check_no_log(self):
        """
        Checks that no logs were found

        :return: nothing
        """
        log_set = LogSet()
        self.assertEquals(len(log_set), 0, "No logs shall be written during such a request")

    def check_log_existence(self):
        """
        Checks for the log existence

        :return: the only log found
        """
        log_set = LogSet()
        self.assertEquals(len(log_set), 1, "There shall be only one log written during the log request")
        for log in log_set:
            return log

    def check_no_log_records(self, log):
        """
        Checks that no log records have been attached to this log

        :param log: the testing log
        :return: nothing
        """
        records = LogRecordSet()
        records.log = log
        self.assertEquals(len(records), 0, "There must be no log record during this test")

    def assert_log_record(self, log, level="INF"):
        """
        Asserts that a certain record has been attached to the log

        :param log: the log which records shall be checked
        :param level: desired record level
        :return: nothing
        """
        records = LogRecordSet()
        records.log = log
        self.assertEquals(len(records), 1, "There must be one record during this test")
        for record in records:
            self.assertEquals(record.level, level, "Wrong record level")
            self.assertGreater(len(record.message), 0, "The record message must not be empty")

    def assert_suggestion(self, response, command_list):
        """
        Asserts that the HTTP response asks the client user to log in using SSH and run proper commands

        :param response: the HTTP response to be asserted
        :param command_list: commands that are required to be mentioned in the response body
        :return: nothing
        """
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST, "Unexpected status code")
        self.assertEquals(response.data['code'], "action_required", "The error reason must be 'action_required'")
        for command in command_list:
            self.assertIn(command, response.data['detail'],
                          "Command '%s' has not been mentioned in the error message" % command)

    def check_two_log_records(self, log):
        """
        Asserts that two log records were attached to a given log

        :param log: the log which records shall be checked
        :return: nothing
        """
        records = LogRecordSet()
        records.log = log
        self.assertEquals(len(records), 2, "There must be exactly two log records during this test")
        for record in records:
            self.assertEquals(record.level, "INF", "Wrong record level")
            self.assertGreater(len(record.message), 0, "The record message must be non-empty")


del BaseViewTest
