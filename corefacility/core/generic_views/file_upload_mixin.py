from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import UploadedFile
from django.core.files.images import ImageFile
from django.utils.translation import gettext as _
from rest_framework.response import Response
from rest_framework.validators import ValidationError


class FileUploadMixin:
    """
    This is a base class for uploading avatars and project data files
    """

    max_file_size = 10 * 1024 * 1024
    """ Maximum file size, in bytes """

    allowed_content_types = None
    """ The file content type shall belong to one of these fields """

    image_formats = {
        "image/jpeg": ["JPEG", "JPEG 2000"],
        "image/jpg": ["JPEG", "JPEG 2000"],
        "image/gif": ["GIF"],
        "image/png": ["PNG"],
    }

    _file_field = None
    """ Defines the file field inside the entity """

    @property
    def file_field(self):
        if self._file_field is None:
            raise NotImplementedError("The '_file_field' property of your view has not been implemented")
        return self._file_field

    def _file_action(self, request, *args, **kwargs):
        """
        File processing
        :param request: The REST framework request
        :param args: position arguments
        :param kwargs: keyword arguments
        :return: The REST framework Response
        """
        if self.detail_serializer_class is None:
            raise NotImplementedError("Please, define the detail_serializer_class to move next")
        if request.method.lower() == "patch":
            return self.upload_file(request)
        if request.method.lower() == "delete":
            return self.delete_file(request)

    def upload_file(self, request):
        """
        Uploads the file

        :param request: The REST framework request
        :return: the REST framework response
        """
        uploaded_file = self.get_file_from_request(request)
        entity = self.get_object()
        if uploaded_file.size > self.max_file_size:
            raise ValidationError(code="file_upload_error", detail=_("The uploaded file is too large"))
        content_type = self.check_file_content_type(uploaded_file)
        processed_file = self.file_preprocessing(entity, uploaded_file, content_type)
        self.attach_file(entity, processed_file)
        entity_serializer = self.detail_serializer_class(entity, context={"request": self.request})
        return Response(entity_serializer.data)

    def delete_file(self, request):
        """
        Deletes the file

        :param request: The REST framework request
        :return: the REST framework response
        """
        entity = self.get_object()
        file_manager = getattr(entity, self.file_field)
        file_manager.detach_file()
        entity_serializer = self.detail_serializer_class(entity, context={"request": self.request})
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

    def file_preprocessing(self, entity, uploaded_file, content_type):
        """
        Changes the file content before file attachment to the entity.
        IMPORTANT: the function shall check that the file content relates to the Content-Type
        :param entity: the entity the file is attached to
        :param uploaded_file: the file before preprocessing
        :param content_type: content-type of the file before preprocessing
        :return: the file after preprocessing
        """
        raise NotImplementedError("SECURITY ALERT: Please, implement the file_preprocessing function that checks the "
                                  "uploaded file for viruses. A simple way to check file for viruses is to open it in"
                                  "numpy, pyeeg and so on (yes, just open and close this file")

    def attach_file(self, entity, attaching_file):
        """
        Saves file to the hard disk drive or to the database

        :param entity: the entity to which the file shall be attached
        :param attaching_file: file to attach (a django.core.files.File instance)
        :return: nothing
        """
        file_manager = getattr(entity, self.file_field)
        file_manager.attach_file(attaching_file)
