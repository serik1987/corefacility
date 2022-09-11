from core.entity.project import ProjectSet
from core.test.views.project_data_test_mixin_small import ProjectDataTestMixinSmall
from imaging.entity import Map
from imaging.models.enums import MapType
from imaging import App as ImagingApp
from roi import App as RoiApp


class MapListMixin(ProjectDataTestMixinSmall):
    """
    Creates the 'map list' environment
    """

    project_maps = None

    application = None

    @classmethod
    def create_test_environment(cls, project_number=2, add_roi_application=False):
        cls.application = ImagingApp()
        if project_number < 2:
            raise ValueError("Number of projects in the map list environment must not be less than 2")
        super().create_test_environment(project_number)
        cls.set_maps()
        if add_roi_application:
            cls.attach_application(RoiApp())

    @classmethod
    def set_maps(cls):
        cls.project_maps = dict()
        for map_info in cls.map_data_provider():
            functional_map = Map(**map_info)
            functional_map.create()
            if functional_map.project.alias not in cls.project_maps:
                cls.project_maps[functional_map.project.alias] = list()
            cls.project_maps[functional_map.project.alias].append(functional_map)

    @classmethod
    def map_data_provider(cls):
        p1 = ProjectSet().get(cls.projects[0])
        p2 = ProjectSet().get(cls.projects[1])
        return [
            dict(alias="c022_X210", type=MapType.orientation, project=p1, width=12400, height=12400),
            dict(alias="c022_X100", type=MapType.direction, project=p1, width=12400, height=12400),
            dict(alias="c023_X2", type=MapType.orientation, project=p1, width=12400, height=12400),
            dict(alias="c025_X300", type=MapType.direction, project=p1, width=12400, height=12400),
            dict(alias="c040_X100", type=MapType.orientation, project=p2, width=12400, height=12400),
            dict(alias="c040_X101", type=MapType.direction, project=p2, width=12400, height=12400),
        ]
