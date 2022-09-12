import os
from io import BytesIO

from django.core.files import File
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.response import Response
import numpy
from numpy.lib.npyio import NpzFile
import scipy
import scipy.io

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

    @action(methods=["GET", "PATCH", "PUT", "POST", "DELETE"], detail=True, url_path="npy", url_name="binary-data")
    def npy(self, request, *args, **kwargs):
        """
        Dealing with binary data
        :param request: the HTTP request that contains the binary data
        :param args: request path arguments
        :param kwargs: request path keyword arguments
        :return: nothing
        """
        if request.method.lower() == "get":
            return self.download_file(request)
        elif request.method.lower() == "delete":
            return self.delete_file(request)
        elif request.method.lower() in ('patch', 'put', 'post'):
            return self.upload_file(request)

    @action(methods=["GET"], detail=True, url_path="mat", url_name="mat-data")
    def mat(self, request, *args, **kwargs):
        """
        Conversion of the binary data to the .mat format
        :param request: the request received from the client application
        :param args: request arguments
        :param kwargs: request keyword arguments
        :return: the response sent to the client application
        """
        return self.download_file(request, processor=self.process_mat)

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
            if os.path.exists(filename):
                os.remove(filename)
        functional_map.data.detach_file()
        map_serializer = self.detail_serializer_class(functional_map, context={"request": self.request})
        return Response(map_serializer.data)

    def download_file(self, request, processor=None):
        """
        Downloads the file
        :param request: request received from the user
        :param processor: some function that accepts filename as first argument and returns the BytesIO object where
            output data will be written
        :return: the response to be sent to the client
        """
        if self.request.project.project_dir is None or not os.path.isdir(self.request.project.project_dir):
            raise ProjectDirNotDefinedException()
        functional_map = self.get_object()
        if functional_map.data.url is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        filename = os.path.join(self.request.project.project_dir, functional_map.data.url)
        if not os.path.exists(filename):
            return Response(status=status.HTTP_204_NO_CONTENT)
        output_stream = (processor if processor is not None else self.process_npy)(filename)
        response = HttpResponse(output_stream.getbuffer(), content_type="application/octet-stream")
        response['Content-Disposition'] = 'attachment; filename="%s"' % functional_map.data.url
        return response

    def process_npy(self, filename):
        """
        Transforms the NUMPY .npy file to the output stream in npy format
        :param filename: full name of a file to be transformed
        :return: the output stream to be saved to the buffer
        """
        output_stream = BytesIO()
        with open(filename, "rb") as npy_file:
            output_stream.write(npy_file.read())
        return output_stream

    def process_mat(self, filename):
        """
        Transforms the NUMPY .npy file to the output stream in .mat format
        :param filename: name of the locally saved .npy file
        :return: the output stream with the data to be sent to the client
        """
        output_stream = BytesIO()
        source_data = numpy.load(filename)
        scipy.io.savemat(output_stream, mdict={"data": source_data})
        return output_stream
