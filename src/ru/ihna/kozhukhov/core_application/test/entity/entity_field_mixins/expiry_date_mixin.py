from datetime import timedelta
from time import sleep


# noinspection PyUnresolvedReferences
class ExpiryDateMixin:
    """
    Provides facilities to test the expiry date.

    General usage:
    @parameterized.expand(base_expiry_date_provider())
    def test_expiry_date_field(self, *args):
        self._test_expiry_date("you_expiry_date_field_name", *args)

    base_expiry_date_provider() is for base test (without automatic destroying of all expired entities)
    extended_expiry_date_provider() is for extended test (testing whether all expired entities can be
        destroyed in one request)
    """

    ENOUGH_INTERVAL_MS = 300

    TEST_EXPIRY_DATE_NOT_SET = 0
    TEST_EXPIRY_DATE_WAS_SET = 1
    TEST_EXPIRY_DATE_WAS_EXPIRED = 2

    def _test_expiry_date(self, field_name, test_number):
        """
        The general test function for the expiry date

        :param field_name: name of the expiry date field to test
        :param test_number: test number
        :return: nothing
        """
        [
            self._test_expiry_date_not_set,
            self._test_expiry_date_was_set,
            self._test_expiry_date_was_expired
        ][test_number](field_name)

    def _test_expiry_date_not_set(self, field_name):
        """
        Tests whether expiry date not set.
        If the expiry date is not set the field shall not be treated as expired

        :param field_name: field name to test
        :return: nothing
        """
        obj = self.get_entity_object_class()()
        obj.create_entity()
        field = getattr(obj.entity, field_name)
        self.assertFalse(field.is_expired(), "The entity is treated as expired but expiry date was not set")

    def _test_expiry_date_was_set(self, field_name):
        obj = self.get_entity_object_class()()
        field = getattr(obj.entity, field_name)
        field.set(timedelta(milliseconds=self.ENOUGH_INTERVAL_MS))
        obj.create_entity()
        obj.reload_entity()
        field = getattr(obj.entity, field_name)
        self.assertFalse(field.is_expired(), "The entity is treated as expired but not enough time was lasted")

    def _test_expiry_date_was_expired(self, field_name):
        obj = self.get_entity_object_class()()
        field = getattr(obj.entity, field_name)
        field.set(timedelta(milliseconds=self.ENOUGH_INTERVAL_MS))
        obj.create_entity()
        sleep(self.ENOUGH_INTERVAL_MS / 1000)
        obj.reload_entity()
        field = getattr(obj.entity, field_name)
        self.assertTrue(field.is_expired(), "When expiration time lasted the entity is still not treated as expired")
