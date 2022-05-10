from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import UploadedFile
from django.core.files.images import ImageFile
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import ValidationError


class AvatarMixin:
    """
    Adds the following action to the viewset:

    upload_avatar (PATCH <basename>/avatar) Uploads the image avatar. The request must have 'multipart/form-data'
        type and request body shall contain exactly one field with an uploaded image
    delete_avatar (DELETE <basename>/avatar) Deletes the image avatar
    """

    allowed_content_types = ["image/jpg", "image/jpeg", "image/gif", "image/png"]
    """ The file content type shall belong to one of these fields """

    image_formats = {
        "image/jpeg": ["JPEG", "JPEG 2000"],
        "image/jpg": ["JPEG", "JPEG 2000"],
        "image/gif": ["GIF"],
        "image/png": ["PNG"],
    }

    desired_image_width = 150
    """ The image will be cut to this width and next downsampled """

    desired_image_height = 150
    """ The image will be cut to this height and next downsampled """

    file_field = "avatar"
    """ Defines the file field inside the entity """

    @action(methods=["PATCH", "DELETE"], detail=True, url_path="avatar", url_name="avatar")
    def avatar(self, request, *args, **kwargs):
        """
        Avatar processing

        :param request: The REST framework request
        :param args: position arguments
        :param kwargs: keyword arguments
        :return: The REST framework Response
        """
        if self.detail_serializer_class is None:
            raise NotImplementedError("Please, define the detail_serializer_class to move next")
        if request.method.lower() == "patch":
            return self.upload_avatar(request)
        if request.method.lower() == "delete":
            return self.delete_avatar(request)

    def upload_avatar(self, request):
        """
        Uploads the avatar

        :param request: The REST framework request
        :return: the REST framework response
        """
        uploaded_file = self.get_file_from_request(request)
        content_type = self.check_file_content_type(uploaded_file)
        processed_file = self.file_preprocessing(uploaded_file, content_type)
        entity = self.get_object()
        self.attach_file(entity, processed_file)
        entity_serializer = self.detail_serializer_class(entity)
        return Response(entity_serializer.data)

    def delete_avatar(self, request):
        """
        Deletes the avatar

        :param request: The REST framework request
        :return: the REST framework response
        """
        entity = self.get_object()
        file_manager = getattr(entity, self.file_field)
        file_manager.detach_file()
        entity_serializer = self.detail_serializer_class(entity)
        return Response(entity_serializer.data)

    def get_file_from_request(self, request):
        """
        Finds a single file in the request and returns it

        :param request: the request which body contains the file
        :return: the file itself
        """
        if len(request.FILES) != 1:
            raise ValidationError(code="file_upload_error",
                                  detail="The file uploading request shall contain exactly one field")
        uploaded_file = None
        for _, uploaded_file in request.FILES.items():
            pass
        if not isinstance(uploaded_file, UploadedFile):
            raise ValidationError(code="file_upload_error",
                                  detail="The uploaded file was not found in the file uploading request")
        return uploaded_file

    def check_file_content_type(self, uploaded_file):
        """
        Checks whether the file has an appropriate content type

        :param uploaded_file: the uploaded file
        :return: content type that the file actually has
        """
        if self.allowed_content_types is None:
            raise NotImplementedError("Please, define the allowed_content_types property due to security reasponse")
        content_type = uploaded_file.content_type
        if content_type not in self.allowed_content_types:
            raise ValidationError(code="file_upload_error",
                                  detail=_("This file type is not uploadable"))
        return content_type

    def file_preprocessing(self, uploaded_file, content_type):
        """
        Executes some file preprocessing actions (e.g., defining that the file has a proper content, changing the
            image resolution etc.)

        :param uploaded_file: the file before preprocessing
        :param content_type: content-type of the file before preprocessing
        :return: the file after preprocessing
        """
        image = Image.open(uploaded_file, "r")
        initial_format = image.format
        if initial_format not in self.image_formats[content_type]:
            raise ValidationError(code="file_upload_error", detail=_("This file type is not uploadable"))
        actual_image_width, actual_image_height = image.size
        if actual_image_width < self.desired_image_width or actual_image_height < self.desired_image_height:
            raise ValidationError(code="file_upload_error", detail=_("The image resolution is too small"))
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

    def attach_file(self, entity, attaching_file):
        """
        Saves file to the hard disk drive or to the database

        :param entity: the entity to which the file shall be attached
        :param attaching_file: file to attach (a django.core.files.File instance)
        :return: nothing
        """
        file_manager = getattr(entity, self.file_field)
        file_manager.attach_file(attaching_file)
