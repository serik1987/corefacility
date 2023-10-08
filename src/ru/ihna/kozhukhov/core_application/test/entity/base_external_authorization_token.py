from .base_test_class import BaseTestClass


class TestExternalAuthorizationToken(BaseTestClass):
    """
    Tests the external authorization tokens
    """

    def test_object_creating_default_plus_changed(self):
        """
        This test case will create new entity then changes some entity fields and at last store entity data
        to the database

        :return: nothing
        """
        pass

    def _check_default_fields(self, token):
        self.assertIsNotNone(token.code, "When the token is not reloaded its authorization code must be available")
        self.assertFieldReceived(token, "authentication")

    def _check_default_change(self, token):
        self.assertFieldReceived(token, "authentication")

    def assertFieldReceived(self, token, field_name):
        if token.state == "creating":
            self.assertIsNone(getattr(token, field_name),
                              "Before call of the create() the field '%s' shall be non-assigned" % field_name)
        else:
            self.assertIsNotNone(getattr(token, field_name),
                                 "After call of the create() the field '%s' shall be assigned" % field_name)


del BaseTestClass
