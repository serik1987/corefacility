from parameterized import parameterized
from django.core.files import File

from core.entity.user import User
from core.entity.group import Group
from core.entity.project import Project
from core.entity.entity_exceptions import EntityDuplicatedException
from core.test.entity.base_test_class import BaseTestClass
from core.test.data_providers.field_value_providers import alias_provider, float_provider, put_stages_in_provider
from core.test.entity.entity_field_mixins.file_field_mixin import FileFieldMixin

from imaging.models.enums import MapType
from imaging.entity import Map
from imaging.tests.data_providers import map_data_provider

from imaging.tests.data_providers.entity_objects.map_object import MapObject


def map_type_provider():
    return put_stages_in_provider([
        ("ori", "ori", None),
        ("dir", "ori", None),
        (MapType.orientation, "ori", None),
        (MapType.direction, "ori", None),
        ("xxx", "ori", ValueError),
        (None, "ori", ValueError),
    ])


class TestMap(FileFieldMixin, BaseTestClass):
    """
    Provides testing routines for the map entity
    """

    _project = None

    _entity_object_class = MapObject

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user = User(login="sergei_kozhukhov")
        user.create()
        group = Group(name="The Main Group", governor=user)
        group.create()
        project = Project(alias="test", name="The Test Project", root_group=group)
        project.create()
        MapObject.define_default_kwarg("project", project)
        cls._project = project

    @parameterized.expand(alias_provider(min_length=1, max_length=50))
    def test_alias(self, *args):
        self._test_field("alias", *args, use_defaults=False, type=MapType.orientation, project=self._project)

    def test_alias_uniqueness(self):
        Map(alias="c022_X210", type=MapType.orientation, project=self._project).create()
        with self.assertRaises(EntityDuplicatedException, msg="The map alias must be unique"):
            Map(alias="c022_X210", type=MapType.direction, project=self._project).create()

    @parameterized.expand(map_data_provider())
    def test_data(self, *args):
        self._test_file_field("data", None, File, *args)

    @parameterized.expand(map_type_provider())
    def test_type(self, *args):
        self._test_field("type", *args, use_defaults=False, alias="c022_X210", project=self._project)

    def test_resolution_x(self):
        self._test_read_only_field("resolution_x", 10)

    def test_resolution_y(self):
        self._test_read_only_field("resolution_y", 10)

    @parameterized.expand(float_provider(min_value=0.0, min_value_enclosed=False))
    def test_map_width(self, *args):
        self._test_field("width", *args)

    @parameterized.expand(float_provider(min_value=0.0, min_value_enclosed=False))
    def test_map_height(self, *args):
        self._test_field("height", *args)

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(entity.alias, "c022_X210", "The map alias was not transmitted correctly")
        self.assertEquals(entity.type, MapType.orientation, "The map type was not transmitted correctly")
        self.assertEquals(entity.data.url, None, "The 'data' field must be None")
        self.assertEquals(entity.project.id, self._project.id, "Unexpected project ID for the functional map")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param entity: the entity to store
        :return: nothing
        """
        self.assertEquals(entity.alias, "c023_X210", "The map alias was not changed")
        self.assertEquals(entity.type, MapType.direction, "The map type was not changed")
        self.assertEquals(entity.data.url, None, "The 'data' field must be None")
        self.assertEquals(entity.project.id, self._project.id, "The project ID must be revealed unchanged")

    def _check_field_consistency(self, obj):
        if "project" in obj.entity_fields:
            self.assertEquals(obj.entity.project.id, obj.entity_fields['project'].id, "Unexpected project ID")
            del obj.entity_fields['project']
        super()._check_field_consistency(obj)


del BaseTestClass
