import os
from io import BytesIO
import struct
import PIL.Image

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

    """
    Resolution of the colorbar for the phase map
    """
    COLORBAR_RESOLUTION = 51
    COLOR_DEPTH = 4
    """ Required by Javascript ImageData object """
    RED_COMPONENT = 0
    GREEN_COMPONENT = 1
    BLUE_COMPONENT = 2
    ALPHA_COMPONENT = 3
    MAX_IMAGE_INTENSITY = 0xFF
    RED_ORIENTATION = 0
    GREEN_ORIENTATION = 2 * numpy.pi / 3
    BLUE_ORIENTATION = -2 * numpy.pi / 3
    ORIENTATION_DISTANCE = 2 * numpy.pi / 3
    """ Difference between two consequtive reference orientations """
    HSV_DEPTH = 3
    HUE_COMPONENT = 0
    SATURATION_COMPONENT = 1
    VALUE_COMPONENT = 2
    MAX_ANGLE = 2 * numpy.pi

    application = App()
    data_gathering_way = "uploading"
    entity_set_class = MapSet
    list_serializer_class = MapSerializer
    detail_serializer_class = MapSerializer
    allowed_content_types = ["application/octet-stream"]
    file_field = "data"

    _harmonic = None

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

    @action(methods=["GET"], detail=True, url_path="bin", url_name="bin-data")
    def bin(self, request, *args, **kwargs):
        """
        Conversion of the binary data to the binary data format, required by the FunctionalMap component
        :param request: the request received from the client application
        :param args: request arguments
        :param kwargs: request keyword arguments
        :return: the response to send to the client
        """
        return self.download_file(request, processor=self.process_bin)

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
        self._harmonic = 1
        if functional_map.type == 'ori':
            self._harmonic = 2
        if functional_map.data.url is None:
            return Response({'detail': "No map file uploaded"}, status=status.HTTP_404_NOT_FOUND)
        filename = os.path.join(self.request.project.project_dir, functional_map.data.url)
        if not os.path.exists(filename):
            return Response({'detail': "The uploaded file has not been found"}, status=status.HTTP_404_NOT_FOUND)
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

    def process_bin(self, filename):
        """
        Transforms the NUMPY .npy file to the output stream suitable for reading by the React JS' FunctionalMapDrawer
        component.

        The output data are binary. For the map with width = W and height = H the structure of the response is the
        following:

        bytes 0-3           'FMAP' string that is used for identification of this file format
        bytes 4-7           map width, px (unsigned integer, big endian). Let's denote it by the letter W
        bytes 8-11          map height, px (unsigned integer, big endian). Let's denote it by the letter H
        bytes 12-19         minimum value in the amplitude map, % (double, big endian)
        bytes 20-27         maximum value in the amplitude map, % (double, big endian)
        bytes 28-31         Resolution of the phase map color bar, px (unsigned integer, big endian). Let's denote it
                            by the letter C
        the following 4*C^2 bytes       Phase color bar (image to draw)
        the following 4*W*H bytes       Amplitude map (image to draw)
        the following 4*W*H bytes       Phase map (image to draw)

        :param filename: full name of the locally saved .npy file
        :return: the standard output stream
        """
        data_input = numpy.load(filename)
        amplitude_map = numpy.abs(data_input)
        phase_map = numpy.angle(data_input) / self._harmonic
        height, width = data_input.shape

        min_value = amplitude_map.min()
        max_value = amplitude_map.max()
        max_size = self.COLORBAR_RESOLUTION // 2
        x_vector = numpy.arange(-max_size, max_size + 1)
        y_vector = numpy.arange(max_size, -max_size - 1, -1)
        x, y = numpy.meshgrid(x_vector, y_vector)
        theta = numpy.arctan2(y, x)
        phase_map_colorbar = self._phase_map_to_rgba(theta)
        alpha_channel = (x * x + y * y <= max_size * max_size) * self.MAX_IMAGE_INTENSITY
        if self._harmonic == 2:
            alpha_channel[x < 0] = 0
        phase_map_colorbar[:, :, self.ALPHA_COMPONENT] = alpha_channel

        amplitude_map_rgba = numpy.zeros((height, width, self.COLOR_DEPTH), dtype=numpy.ubyte)
        amplitude_map_rgba[:, :, self.RED_COMPONENT] = amplitude_map_rgba[:, :, self.GREEN_COMPONENT] = \
            amplitude_map_rgba[:, :, self.BLUE_COMPONENT] = \
            self.MAX_IMAGE_INTENSITY * (amplitude_map - min_value) / (max_value - min_value)
        amplitude_map_rgba[:, :, self.ALPHA_COMPONENT] = self.MAX_IMAGE_INTENSITY

        phase_map_rgba = self._phase_map_to_rgba(phase_map)

        data_output = BytesIO()
        data_output.write(struct.pack(
            '!4sLLddL',
            b'FMAP', data_input.shape[1], data_input.shape[0], min_value, max_value, self.COLORBAR_RESOLUTION
        ))
        data_output.write(phase_map_colorbar)
        data_output.write(amplitude_map_rgba.tobytes('C'))
        data_output.write(phase_map_rgba)

        return data_output

    def _phase_map_to_rgba(self, phase_map: numpy.array) -> numpy.array:
        """
        Represents phase map as sRGB bitmap using the HSV colormap
        :param phase_map: orientations or another phase values in radians
        :return: the sRGB bitmap itself. Such a bitmap must be written to the response output stream when is processed
            on the server side and must be transformed to Javascript's Uint8ClampedArray and next to the Javascript's
            ImageData when is processed on the client side
        """
        height, width = phase_map.shape
        hue_map = phase_map * self._harmonic
        hsv_map = numpy.zeros((height, width, self.HSV_DEPTH), dtype=numpy.ubyte)
        hsv_map[:, :, self.HUE_COMPONENT] = hue_map * self.MAX_IMAGE_INTENSITY / self.MAX_ANGLE
        hsv_map[:, :, self.SATURATION_COMPONENT] = hsv_map[:, :, self.VALUE_COMPONENT] = self.MAX_IMAGE_INTENSITY
        hsv_map_raw = hsv_map.tobytes('C')
        hsv_image = PIL.Image.frombytes('HSV', (width, height), hsv_map_raw)
        rgba_image = hsv_image.convert('RGBA')
        rgba_map_raw = rgba_image.tobytes()
        rgba_map = numpy    \
            .frombuffer(rgba_map_raw, dtype=numpy.ubyte)    \
            .reshape((height, width, self.COLOR_DEPTH), order='C')
        return numpy.copy(rgba_map)

    def _get_colored_orientations(self, ordinary_orientations, base_orientation):
        """
        To be used solely by the _phase_map_to_rgba method.
        Fills a single color channel in the sRGB bitmap (not suitable for alpha channel).
        :param ordinary_orientations: the source phase map
        :param base_orientation: a phase the is represented by the value 255 of the color channel considered.
        :return: the channel values as 2D array
        """
        relative_orientations = ordinary_orientations - base_orientation
        low_overflow_pixels = relative_orientations < -numpy.pi / self._harmonic
        relative_orientations[low_overflow_pixels] += 2 * numpy.pi / self._harmonic
        high_overflow_pixels = relative_orientations > numpy.pi / self._harmonic
        relative_orientations[high_overflow_pixels] -= 2 * numpy.pi / self._harmonic
        color = self.MAX_IMAGE_INTENSITY * \
            (1 - numpy.abs(relative_orientations) * self._harmonic / self.ORIENTATION_DISTANCE)
        color[color < 0.0] = 0.0
        return color
