from datetime import datetime

from django.test import TestCase
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_record.complex_interval import ComplexInterval


class TestComplexInterval(TestCase):
    """
    Tests the complex interval features
    """

    @parameterized.expand([
        (datetime(2000, 1, 1), float('inf'), True,
            None, False, False, True, True, True, True, True, True, True,),
        (datetime(2000, 1, 1), -float('inf'), False,
            ValueError, None, None, None, None, None, None, None, None, None,),
        (datetime(2000, 1, 1,), datetime(2001, 1, 1), False,
            None, True, True, True, False, False, False, True, True, True,),
        (datetime(2000, 1, 1,), datetime(2001, 1, 1), True,
            None, False, False, True, True, True, True, True, False, False),
        (float('inf'), datetime(2001, 1, 1), True,
            ValueError, None, None, None, None, None, None, None, None, None,),
        (float('inf'), -float('inf'), False,
            ValueError, None, None, None, None, None, None, None, None, None,),
        (-float('inf'), float('inf'), False,
            None, False, False, False, False, False, False, False, False, False,),
        (float('-inf'), float('-inf'), True,
            None, False, False, False, False, False, False, False, False, False,),
        (float('-inf'), datetime(2001, 1, 1), True,
            None, True, True, True, True, True, True, True, False, False),
    ])
    def test_simple_interval(self, low, high, contains, result, t1, t2, t3, t4, t5, t6, t7, t8, t9):
        """
        Tests the simple interval

        :param low: the low interval bound
        :param high: the high interval bound
        :param contains: the third argument
        """
        def wrapped():
            return ComplexInterval(low, high, contains)
        if result is None:
            interval = wrapped()
            self.assertEquals(datetime(1995, 1, 1) in interval, t1, "Malformed interval")
            self.assertEquals(datetime(1999, 12, 31) in interval, t2, "Malformed interval")
            self.assertEquals(datetime(2000, 1, 1) in interval, t3, "Malformed interval")
            self.assertEquals(datetime(2000, 1, 2) in interval, t4, "Malformed interval")
            self.assertEquals(datetime(2000, 6, 1) in interval, t5, "Malformed interval")
            self.assertEquals(datetime(2000, 12, 31) in interval, t6, "Malformed interval")
            self.assertEquals(datetime(2001, 1, 1) in interval, t7, "Malformed interval")
            self.assertEquals(datetime(2001, 1, 2) in interval, t8, "Malformed interval")
            self.assertEquals(datetime(2005, 1, 1) in interval, t9, "Malformed interval")
        else:
            self.assertRaises(result, wrapped)

    def test_and_operation_separate(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1))
        interval2 = ComplexInterval(datetime(2002, 1, 1), datetime(2003, 1, 1))
        interval = interval1 & interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertFalse(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2001, 12, 31) in interval)
        self.assertFalse(datetime(2002, 1, 1) in interval)
        self.assertFalse(datetime(2002, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertFalse(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_or_operation_separate(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1))
        interval2 = ComplexInterval(datetime(2002, 1, 1), datetime(2003, 1, 1))
        interval = interval1 | interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertTrue(datetime(2002, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_and_operation_separate_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), False)
        interval2 = ComplexInterval(datetime(2002, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 & interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertFalse(datetime(2002, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_or_operation_separate_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), False)
        interval2 = ComplexInterval(datetime(2002, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 | interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertTrue(datetime(2002, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_and_operation_one_point(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), True)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1), True)
        interval = interval1 & interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertFalse(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_or_operation_one_point(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), True)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1), True)
        interval = interval1 | interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_and_operation_one_point_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), False)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 & interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_or_operation_one_point_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), False)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 | interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_and_operation_cross(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2002, 1, 1), False)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 & interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertFalse(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2001, 12, 31) in interval)
        self.assertFalse(datetime(2002, 1, 1) in interval)
        self.assertFalse(datetime(2002, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_or_operation_cross(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2002, 1, 1))
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1))
        interval = interval1 | interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertTrue(datetime(2002, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_or_operation_cross_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2002, 1, 1), False)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 | interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertTrue(datetime(2002, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_and_operation_one_point_out(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), True)
        interval2 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1), True)
        interval = interval1 & interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertFalse(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_or_operation_one_point_out(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), True)
        interval2 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1), True)
        interval = interval1 | interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_and_operation_one_point_out_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), False)
        interval2 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 & interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertFalse(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_or_operation_one_point_out_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2001, 1, 1), False)
        interval2 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1), False)
        interval = interval1 | interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_and_operation_inside(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1))
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2002, 1, 1))
        interval = interval1 & interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertFalse(datetime(2002, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertFalse(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_or_operation_inside(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1))
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2002, 1, 1))
        interval = interval1 | interval2
        self.assertFalse(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertTrue(datetime(2001, 1, 2) in interval)
        self.assertTrue(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertTrue(datetime(2002, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertFalse(datetime(2003, 1, 2) in interval)

    def test_and_operation_inside_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1), False)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2002, 1, 1), False)
        interval = interval1 & interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertFalse(datetime(2000, 1, 2) in interval)
        self.assertFalse(datetime(2000, 12, 31) in interval)
        self.assertFalse(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2001, 12, 31) in interval)
        self.assertFalse(datetime(2002, 1, 1) in interval)
        self.assertFalse(datetime(2002, 1, 2) in interval)
        self.assertFalse(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)

    def test_or_operation_inside_inverse(self):
        interval1 = ComplexInterval(datetime(2000, 1, 1), datetime(2003, 1, 1), False)
        interval2 = ComplexInterval(datetime(2001, 1, 1), datetime(2002, 1, 1), False)
        interval = interval1 | interval2
        self.assertTrue(datetime(1999, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 1) in interval)
        self.assertTrue(datetime(2000, 1, 2) in interval)
        self.assertTrue(datetime(2000, 12, 31) in interval)
        self.assertTrue(datetime(2001, 1, 1) in interval)
        self.assertFalse(datetime(2001, 1, 2) in interval)
        self.assertFalse(datetime(2001, 12, 31) in interval)
        self.assertTrue(datetime(2002, 1, 1) in interval)
        self.assertTrue(datetime(2002, 1, 2) in interval)
        self.assertTrue(datetime(2002, 12, 31) in interval)
        self.assertTrue(datetime(2003, 1, 1) in interval)
        self.assertTrue(datetime(2003, 1, 2) in interval)
