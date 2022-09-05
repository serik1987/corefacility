import io
import os
import numpy
from django.urls import reverse
from django.core.files import File
from rest_framework.exceptions import NotFound

from core.generic_views import EntityViewMixin
from core.entity.entity_exceptions import EntityNotFoundException
from imaging.entity import Map, MapSet
from imaging.api_exceptions import *


class FunctionalMapMixin(EntityViewMixin):
    """
    The base class for all views dealing with functional map processing
    """

    def filter_queryset(self, entity_set):
        """
        Provides additional filtration of the pinwheel set
        :param entity_set: the pinwheel set before the filtration
        :return: the pinwheel set after the filtration
        """
        map_set = MapSet()
        map_set.project = self.request.project
        try:
            map_lookup = int(self.kwargs['map_lookup'])
        except ValueError:
            map_lookup = self.kwargs['map_lookup']
        try:
            self.request.functional_map = map_set.get(map_lookup)
        except EntityNotFoundException:
            raise NotFound()
        entity_set = super().filter_queryset(entity_set)
        entity_set.map = self.request.functional_map
        return entity_set

    def load_map_data(self):
        """
        Loads the map data from the hard disk drive
        :return: numpy's 2D array containing the loaded map
        """
        project_dir = self.request.project.project_dir
        if project_dir is None or not os.path.isdir(project_dir):
            raise ProjectDirNotDefinedException()
        map_file = self.request.functional_map.data.url
        if map_file is None:
            raise MapNotUploadedException()
        map_full_file = os.path.join(project_dir, map_file)
        try:
            source_data = numpy.load(map_full_file)
        except OSError:
            raise UploadFileMissingException()
        return source_data

    def save_map_data(self, alias, data):
        """
        Creates new Map entity that contains data processing results
        :param alias: new alias of the map. Must be distinguished from the old alias
        :param data: numpy's 2D array containing the saved map
        :return: URL of the saved entity. You can use such URL for redirection response
        """
        if data.size == 0:
            raise TargetMapEmptyException()
        resolution_y, resolution_x = data.shape
        new_functional_map = Map(
            alias=alias,
            type=self.request.functional_map.type,
            width=self.request.functional_map.width * resolution_x / self.request.functional_map.resolution_x,
            height=self.request.functional_map.height * resolution_y / self.request.functional_map.resolution_y,
            project=self.request.project
        )
        new_functional_map._set_resolution(resolution_x, resolution_y)
        new_functional_map.create()
        output_stream = io.BytesIO()
        numpy.save(output_stream, data)
        filename = "%s.npy" % alias
        map_file = File(output_stream, name=filename)
        new_functional_map.data.attach_file(map_file)
        full_name = os.path.join(self.request.project.project_dir, filename)
        with open(full_name, "wb") as output_file:
            output_file.write(map_file.file.getbuffer())
        return reverse("core:projects:imaging:functional-map-detail",
                       kwargs={
                           "version": self.kwargs['version'],
                           "project_lookup": self.request.project.alias,
                           "lookup": alias
                       })
