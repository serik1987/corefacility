from django.test import TestCase

from core.entity.entity_providers.posix_providers.posix_provider import PosixProvider

from .media_files_mixin import MediaFilesMixin


class MediaFilesTestCase(MediaFilesMixin, TestCase):
    """
    The base class for all test cases that deals with media files.

    Please, be attentive that the class implements methods setUpTestData, tearDownClass and tearDown methods.
    Use super() if you want to override them in your derived class.
    """

    posix_disabled = True
    """ True if POSIX features are not going to be tested, False otherwise """

    @classmethod
    def setUpTestData(cls):
        if cls.posix_disabled:
            PosixProvider.force_disable = True
        super().setUpTestData()
        cls.create_media_root_backup()

    def tearDown(self):
        self.clear_media_root()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.restore_media_root_backup()
        super().tearDownClass()
        PosixProvider.force_disable = False
