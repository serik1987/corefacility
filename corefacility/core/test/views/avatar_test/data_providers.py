import os

from django.conf import settings
from rest_framework import status


class FileUploadProvider:
    """
    This is a collection of all providers that will be used in the file uploading tests
    """

    @staticmethod
    def sample_image_provider(extension=".jpg"):
        """
        Provides a sample file data

        :param extension: an extension of the file
        :return: full file name
        """
        image_dir = FileUploadProvider.get_image_dir()
        out_name = None
        for filename in os.listdir(image_dir):
            fullname = os.path.join(image_dir, filename)
            if os.path.isfile(fullname) and filename.endswith(extension):
                out_name = fullname
                break
        return out_name

    @staticmethod
    def all_image_provider():
        """
        Returns all images plus one non-valid file

        :return: list of the argument tuples
        """
        all_images = []
        image_dir = FileUploadProvider.get_image_dir()
        for filename in os.listdir(image_dir):
            fullname = os.path.join(image_dir, filename)
            if os.path.isfile(fullname):
                all_images.append((fullname, status.HTTP_200_OK))
        wrong_file_dir = FileUploadProvider.get_wrong_file_dir()
        for filename in os.listdir(wrong_file_dir):
            wrong_file = os.path.join(wrong_file_dir, filename)
            if os.path.isfile(wrong_file):
                all_images.append((wrong_file, status.HTTP_400_BAD_REQUEST))
        return all_images

    @staticmethod
    def get_image_dir():
        """
        Returns an image directory

        :return: a string containing the image directory
        """
        return os.path.join(settings.BASE_DIR, "core/test/data_providers/images")

    @staticmethod
    def get_wrong_file_dir():
        """
        Returns the directory of wrong file (e.g., pdf's)

        :return: durectory of wrong files
        """
        return os.path.join(settings.BASE_DIR, "core/test/data_providers/pdf")
