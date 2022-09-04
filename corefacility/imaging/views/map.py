import os
from io import BytesIO

from django.core.files import File
from rest_framework.decorators import action
from rest_framework.response import Response
import numpy
from numpy.lib.npyio import NpzFile

from core.generic_views import EntityViewSet, FileUploadMixin
from core.api_exceptions import FileFormatException
from imaging import App
from imaging.entity import MapSet
from imaging.serializers import MapSerializer
from imaging.api_exceptions import *


class MapViewSet(FileUploadMixin, EntityViewSet):
    """
    Working with functional maps
    """

    application = App()
    data_gathering_way = "uploading"
    entity_set_class = MapSet
    list_serializer_class = MapSerializer
    detail_serializer_class = MapSerializer
    allowed_content_types = ["application/octet-stream"]
    file_field = "data"

    @action(methods=["PATCH", "DELETE"], detail=True, url_path="npy", url_name="binary-data")
    def npy(self, request, *args, **kwargs):
        """
        Dealing with binary data
        :param request: the HTTP request that contains the binary data
        :param args: request path arguments
        :param kwargs: request path keyword arguments
        :return: nothing
        """
        return self._file_action(request, *args, **kwargs)

    def filter_queryset(self, map_set):
        """
        Applies additional filtration to the map set
        :param map_set: the map set before filtration
        :return: the map set after filtration
        """
        map_set = super().filter_queryset(map_set)
        map_set.project = self.request.project
        return map_set

    # noinspection PyTypeChecker
    def file_preprocessing(self, map_entity, uploaded_file, content_type):
        """
        Ensures that the file have proper (NPZ) type
        :param map_entity: the map entity that shall be attached to this functional map
        :param uploaded_file: the file before preprocessing
        :param content_type: content-type of the file before preprocessing
        :return: the file after preprocessing
        """
        try:
            imaging_data = numpy.load(uploaded_file)
        except ValueError:
            raise FileFormatException()
        if isinstance(imaging_data, NpzFile):
            if len(imaging_data.files) != 1:
                imaging_data.close()
                raise DataNumberException()
            arr = imaging_data[imaging_data.files[0]]
            imaging_data.close()
            imaging_data = arr
        if not isinstance(imaging_data, numpy.ndarray) or imaging_data.ndim != 2 or imaging_data.size == 0 or \
                not str(imaging_data.dtype).startswith("complex"):
            raise NotAMapException()
        resolution_y, resolution_x = imaging_data.shape
        map_entity._set_resolution(resolution_x, resolution_y)
        map_entity.update()
        imaging_data_stream = BytesIO()
        numpy.save(imaging_data_stream, imaging_data)
        processed_file = File(imaging_data_stream, name="%s.npy" % map_entity.alias)
        return processed_file

    def attach_file(self, functional_map, attaching_file):
        """
        Saves file to the hard disk drive or to the database
        :param functional_map: the entity to which the file shall be attached
        :param attaching_file: file to attach (a django.core.files.File instance)
        :return: nothing
        """
        super().attach_file(functional_map, attaching_file)
        if self.request.project.project_dir is None or not os.path.isdir(self.request.project.project_dir):
            raise ProjectDirNotDefinedException()
        filename = os.path.join(self.request.project.project_dir, functional_map.data.url)
        with open(filename, "wb") as file_object:
            file_object.write(attaching_file.file.getbuffer())

    def delete_file(self, request):
        """
        Deletes the file
        :param request: The REST framework request
        :return: the REST framework response
        """
        if self.request.project.project_dir is None or not os.path.isdir(self.request.project.project_dir):
            raise ProjectDirNotDefinedException()
        functional_map = self.get_object()
        if functional_map.data.url is not None:
            filename = os.path.join(self.request.project.project_dir, functional_map.data.url)
            os.remove(filename)
        functional_map.data.detach_file()
        map_serializer = self.detail_serializer_class(functional_map, context={"request": self.request})
        return Response(map_serializer.data)
