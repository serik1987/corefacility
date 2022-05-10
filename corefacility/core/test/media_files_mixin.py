import os
import shutil

from django.conf import settings


class MediaFilesMixin:
    """
    This is a simple mixin that contains some auxiliary facilities for the file uploading
    """

    @staticmethod
    def create_media_root_backup():
        """
        Creates the backup of the media files directory which prevents the media files from being damaged.

        :return: nothing
        """
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

    @staticmethod
    def clear_media_root():
        """
        Clears all files in the media root except the backup created by the create_media_root() routine.

        :return: nothing
        """
        for file in os.listdir(settings.MEDIA_ROOT):
            full_name = os.path.join(settings.MEDIA_ROOT, file)
            if os.path.isfile(full_name):
                os.unlink(full_name)

    @staticmethod
    def restore_media_root_backup():
        """
        Restores the media root from the backup created by means of create_media_root_backup routine

        :return: nothing
        """
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
