from pathlib import Path
from imaging import App as ImagingApp

from .base_application_permissions_test import *


TestApplicationPermission = generate_test_class(
    arg_entity_create_file=Path(__file__).parent / "test_cases/imaging_map_create.csv",
    arg_entity_update_file=Path(__file__).parent / "test_cases/imaging_map_update.csv",
    arg_entity_get_file=Path(__file__).parent / "test_cases/imaging_map_view.csv",
    arg_entity_destroy_file=Path(__file__).parent / "test_cases/imaging_map_delete.csv",
    arg_include_create_test=True,
    arg_include_update_test=True,
    arg_include_get_test=True,
    arg_include_destroy_test=True
)


class TestImagingPermission(TestApplicationPermission):
    """
    Provides testing imaging permissions
    """

    ENTITY_APPLICATION_CLASS = ImagingApp
    ENTITY_LIST_PATH = "/api/{version}/core/projects/{project_alias}/imaging/data/"
    ENTITY_DETAIL_PATH = "/api/{version}/core/projects/{project_alias}/imaging/data/{data_alias}/"

    SOURCE_DATA = {
        "alias": "c023_X210",
        "type": "ori",
    }

    UPDATED_DATA = {"type": "dir"}

    def create_test_entity(self, project_alias):
        project = self._project_set_object.get_by_alias(project_alias)
        functional_map = Map(**self.SOURCE_DATA)
        functional_map.project = project
        functional_map.create()
        return functional_map.id


del TestApplicationPermission
