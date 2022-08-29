from core.test.sample_log_mixin import SampleLogMixin

from .base_test_class import BaseTestClass


class BaseLogTest(SampleLogMixin, BaseTestClass):
    """
    Defines the base class for read-only requests, such as /api/v1/log/ or /api/v1/log/<id>/records/
    """

    superuser_required = True
    ordinary_user_required = True


del BaseTestClass
