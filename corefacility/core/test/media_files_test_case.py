from django.test import TestCase

from .media_files_mixin import MediaFilesMixin


class MediaFilesTestCase(MediaFilesMixin, TestCase):
    """
    The base class for all test cases that deals with media files.

    Please, be attentive that the class implements methods setUpTestData, tearDownClass and tearDown methods.
    Use super() if you want to override them in your derived class.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_media_root_backup()

    def tearDown(self):
        self.clear_media_root()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.restore_media_root_backup()
        super().tearDownClass()
