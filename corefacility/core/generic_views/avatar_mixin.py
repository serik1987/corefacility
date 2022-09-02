from io import BytesIO

from PIL import Image
from django.core.files.images import ImageFile
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from core.api_exceptions import FileFormatException, AvatarResolutionTooSmallException
from .file_upload_mixin import FileUploadMixin


class AvatarMixin(FileUploadMixin):
    """
    Adds the following action to the viewset:

    upload_avatar (PATCH <basename>/avatar) Uploads the image avatar. The request must have 'multipart/form-data'
        type and request body shall contain exactly one field with an uploaded image
    delete_avatar (DELETE <basename>/avatar) Deletes the image avatar
    """

    allowed_content_types = ["image/jpg", "image/jpeg", "image/gif", "image/png"]
    """ The file content type shall belong to one of these fields """

    _file_field = "avatar"
    """ Defines the file field inside the entity """

    desired_image_width = 150
    """ The image will be cut to this width and next downsampled """

    desired_image_height = 150
    """ The image will be cut to this height and next downsampled """

    @action(methods=["PATCH", "DELETE"], detail=True, url_path="avatar", url_name="avatar")
    def avatar(self, request, *args, **kwargs):
        """
        Avatar processing
        :param request: The REST framework request
        :param args: position arguments
        :param kwargs: keyword arguments
        :return: The REST framework Response
        """
        return self._file_action(request, *args, **kwargs)

    def file_preprocessing(self, entity, uploaded_file, content_type):
        """
        Executes some file preprocessing actions (e.g., defining that the file has a proper content, changing the
            image resolution etc.)
        :param entity: the entity the file shall be attached to. The entity shall be already created
        :param uploaded_file: the file before preprocessing
        :param content_type: content-type of the file before preprocessing
        :return: the file after preprocessing
        """
        image = Image.open(uploaded_file, "r")
        initial_format = image.format
        if initial_format not in self.image_formats[content_type]:
            raise FileFormatException()
        actual_image_width, actual_image_height = image.size
        if actual_image_width < self.desired_image_width or actual_image_height < self.desired_image_height:
            raise AvatarResolutionTooSmallException()
        downsample_ratio = min(actual_image_width / self.desired_image_width,
                               actual_image_height / self.desired_image_height)
        thumbnailed_width = int(actual_image_width / downsample_ratio)
        thumbnailed_height = int(actual_image_height / downsample_ratio)
        image.thumbnail((thumbnailed_width, thumbnailed_height))
        if thumbnailed_height > self.desired_image_height:
            image = image.crop((0, 0, self.desired_image_width, self.desired_image_height))
        if thumbnailed_width > self.desired_image_width:
            delta = (thumbnailed_width - self.desired_image_width) // 2
            image = image.crop((delta, 0, delta + self.desired_image_width, self.desired_image_height))
        image_stream = BytesIO()
        image.save(image_stream, format=initial_format)
        processed_file = ImageFile(image_stream, name=uploaded_file.name)
        return processed_file
