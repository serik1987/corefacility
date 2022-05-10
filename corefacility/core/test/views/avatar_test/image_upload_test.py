from PIL import Image
from parameterized import parameterized

from .file_upload_test import FileUploadTest
from .data_providers import FileUploadProvider


class ImageUploadTest(FileUploadTest):
    """
    A base class for image upload and delete tests
    """

    sample_file = FileUploadProvider.sample_image_provider()
    sample_file_2 = FileUploadProvider.sample_image_provider(extension=".gif")

    desired_image_size = None
    """ A tuple that contains image width and height respectively """

    @parameterized.expand(FileUploadProvider.all_image_provider())
    def test_valid_upload_type(self, filename, expected_status_code):
        self._test_valid_upload_type(filename, expected_status_code)

    def test_image_size(self):
        """
        Tests that the image has been resized to the desired values after uploading

        :return: nothing
        """
        sample_image = self.get_sample_file()
        response = self.upload(sample_image)
        uploaded_file = self.assert_database(response)
        with Image.open(uploaded_file) as im:
            self.assertEquals(im.size, self.get_desired_image_size())

    def get_desired_image_size(self):
        if self.desired_image_size is None:
            raise NotImplementedError("Please, define the 'desired_image_size' property")
        return self.desired_image_size


del FileUploadTest
