from pathlib import Path
from imaging.entity import Map, MapSet
from roi import App as RoiApp
from roi.entity import Pinwheel

from .base_application_permissions_test import generate_test_class


TestApplicationPermissions = generate_test_class(
    arg_entity_create_file=Path(__file__).parent / "test_cases/roi_create.csv",
    arg_entity_update_file=Path(__file__).parent / "test_cases/roi_detail.csv",
    arg_entity_get_file=Path(__file__).parent / "test_cases/roi_detail.csv",
    arg_entity_destroy_file=Path(__file__).parent / "test_cases/roi_delete.csv",
    arg_include_create_test=True,
    arg_include_update_test=True,
    arg_include_get_test=True,
    arg_include_destroy_test=True
)


class TestRoiPermissions(TestApplicationPermissions):
    """
    Testing ROI permissions
    """

    ENTITY_APPLICATION_CLASS = RoiApp

    ENTITY_LIST_PATH = \
        "/api/{version}/core/projects/{project_alias}/imaging/processors/{project_alias}_map/roi/pinwheels/"

    ENTITY_DETAIL_PATH =\
        "/api/{version}/core/projects/{project_alias}/imaging/processors/{project_alias}_map/roi/pinwheels/" \
        "{data_alias}/"

    SOURCE_DATA = {"x": 200, "y": 300}

    UPDATED_DATA = {"x": 150}

    functional_maps = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.functional_maps = dict()
        for project in cls._project_set_object:
            functional_map = Map(alias="%s_map" % project.alias, type="ori", project=project)
            functional_map.create()
            cls.functional_maps[project.alias] = functional_map

    def create_test_entity(self, project_alias):
        """
        We need to create tested entity for PUT/PATCH, GET and DELETE requests
        :param project_alias: alias of the project where test entity shall be created
        :return: nothing
        """
        functional_map = self.functional_maps[project_alias]
        pinwheel = Pinwheel(**self.SOURCE_DATA)
        pinwheel.map = functional_map
        pinwheel.create()
        return pinwheel.id


del TestApplicationPermissions
