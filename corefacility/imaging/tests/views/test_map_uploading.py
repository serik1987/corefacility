from pathlib import Path

from core.test.views.project_data_test_mixin_small import ProjectDataTestMixinSmall
from core.test.views.field_test.base_test_class import BaseTestClass
from imaging import App
from imaging.entity import Map


class TestMapUploading(ProjectDataTestMixinSmall, BaseTestClass):
    """
    Tests whether the map can be successfully uploaded or deleted
    """

    application = App()
    functional_map = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_test_environment()
        cls.functional_map = Map(alias="c023_X210", type="ori", project=cls.project)
        cls.functional_map.create()

    def test_sample(self):
        filename = Path(__file__).parent.parent / "data_providers/sample_maps/c010_ori00_filt.npz"
        headers = self.get_authorization_headers("superuser")
        with open(filename, "rb") as fp:
            detail_path = "/api/v1/core/projects/test_project/imaging/data/c023_X210/npy/"
            response = self.client.patch(detail_path, {"file": fp}, format="multipart", **headers)
            print(response, response.data)
