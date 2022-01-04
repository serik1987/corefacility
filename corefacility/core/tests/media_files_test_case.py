import os
import shutil

from django.conf import settings
from django.test import TestCase


class MediaFilesTestCase(TestCase):
    """
    The base class for all test cases that deals with media files.

    Please, be attentive that the class implements methods setUpTestData, tearDownClass and tearDown methods.
    Use super() if you want to override them in your derived class.
    """

    @classmethod
    def setUpTestData(cls):
        root = settings.MEDIA_ROOT
        root_copy = os.path.join(root, "original")
        try:
            os.mkdir(root_copy)
        except FileExistsError:
            pass
        for filename in os.listdir(root):
            fullname = os.path.join(root, filename)
            if os.path.isfile(fullname):
                new_name = os.path.join(root_copy, filename)
                shutil.move(fullname, new_name)

    def tearDown(self) -> None:
        for file in os.listdir(settings.MEDIA_ROOT):
            full_name = os.path.join(settings.MEDIA_ROOT, file)
            if os.path.isfile(full_name):
                os.unlink(full_name)

    @classmethod
    def tearDownClass(cls):
        try:
            root = settings.MEDIA_ROOT
            root_copy = os.path.join(root, "original")
            for filename in os.listdir(root_copy):
                src = os.path.join(root_copy, filename)
                dst = os.path.join(root, filename)
                shutil.move(src, dst)
            os.rmdir(root_copy)
        except FileNotFoundError:
            raise FileNotFoundError("The 'original' directory doesn't exist in your media root. "
                                    "Did you forget to call setUpTestData() method in the superclass when overriding "
                                    "setUpTestData method for your class?")
