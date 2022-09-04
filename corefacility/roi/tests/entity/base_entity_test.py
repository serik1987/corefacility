from core.entity.user import User
from core.entity.group import Group
from core.entity.project import Project
from imaging.entity import Map
from core.test.entity.base_test_class import BaseTestClass


class BaseEntityTest(BaseTestClass):

    _related_user = None
    _related_group = None
    _related_project = None
    _related_map = None
    _another_map = None
    _creating_map = None
    _map_list = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._related_user = User(login="user")
        cls._related_user.create()
        cls._related_group = Group(name="group", governor=cls._related_user)
        cls._related_group.create()
        cls._related_project = Project(alias="project", name="project", root_group=cls._related_group)
        cls._related_project.create()
        cls._related_map = Map(alias="c022_X210", type="ori", project=cls._related_project)
        cls._related_map.create()
