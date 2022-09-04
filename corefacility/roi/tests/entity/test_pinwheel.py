from parameterized import parameterized

from core.entity.entity_exceptions import EntityFieldInvalid
from core.test.data_providers.field_value_providers import integer_provider, put_stages_in_provider
from imaging.entity import Map
from roi.tests.entity_objects.pinwheel_object import PinwheelObject

from .base_entity_test import BaseEntityTest


def map_provider():
    return put_stages_in_provider([
        (0, 1, None),
        (2, 1, RuntimeError),
        (None, 1, EntityFieldInvalid),
    ])


class TestPinwheel(BaseEntityTest):
    """
    Provides test routines for a single pinwheel
    """

    _entity_object_class = PinwheelObject

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        PinwheelObject.define_default_kwarg("map", cls._related_map)
        cls._another_map = Map(alias="c023_X210", type="dir", project=cls._related_project)
        cls._another_map.create()
        cls._creating_map = Map(alias="c024_X210", type="ori", project=cls._related_project)
        cls._map_list = [cls._related_map, cls._another_map, cls._creating_map]

    @parameterized.expand(integer_provider(min_value=0))
    def test_x(self, *args):
        self._test_field("x", *args, use_defaults=False, y=210, map=self._related_map)

    @parameterized.expand(integer_provider(min_value=0))
    def test_y(self, *args):
        self._test_field("y", *args, use_defaults=False, x=140, map=self._related_map)

    @parameterized.expand(map_provider())
    def test_map(self, value, other_value, throwing_exception, step_number):
        """
        Tests the map field for validity
        :param value: value for the map field
        :param other_value: another value field
        :param throwing_exception: exception to throw
        :param step_number: step number
        """
        if value is not None:
            value = self._map_list[value]
        if other_value is not None:
            other_value = self._map_list[other_value]
        self._test_field("map", value, other_value, throwing_exception, step_number)

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(entity.x, 141, "The pinwheel abscissa was not correctly transmitted")
        self.assertEquals(entity.y, 210, "The pinwheel ordinate was not correctly transmitted")
        self.assertEquals(entity.map.id, self._related_map.id, "The belonging map was not correctly transmitted")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly change.
        The method deals with default data only.

        :param entity: the entity to store
        :return: nothing
        """
        self.assertEquals(entity.x, 400, "The pinwheel abscissa was not correctly changed")
        self.assertEquals(entity.y, 500, "The pinwheel ordinate was not correctly changed")


del BaseEntityTest
