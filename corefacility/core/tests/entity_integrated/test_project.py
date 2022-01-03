import warnings

from parameterized import parameterized

from core.models import Project as ProjectModel
from core.entity.group import Group
from core.entity.user import User
from core.tests.data_providers.field_value_providers import alias_provider
from .base_test_class import BaseTestClass
from .entity_objects.project_object import ProjectObject


class TestProject(BaseTestClass):
    """
    Provides immediate project testing
    """

    _entity_object_class = ProjectObject
    """ All entity that will be created in this test case are Projects """

    _entity_model_class = ProjectModel
    """ The entity model class is a Django model that is used for storing entities """

    __related_user = None
    """ The user the is intended to be the project leader """

    __related_group = None
    """ Defines the governing group of the project """

    @classmethod
    def setUpTestData(cls):
        cls.__related_user = User(login="sergei.kozhukhov")
        cls.__related_user.create()
        cls.__related_group = Group(name="Оптическое картирование", governor=cls.__related_user)
        cls.__related_group.create()
        ProjectObject.define_default_kwarg("root_group", cls.__related_group)

    @parameterized.expand(alias_provider(1, 64))
    def test_alias(self, value, updated_value, exception_to_throw, route_number):
        self._test_field("alias", value, updated_value, exception_to_throw, route_number,
                         use_defaults=False, name="Некий тестовый проект", root_group=self.__related_group)

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(entity.alias, "vasomotor-oscillations")
        self.assertEquals(entity.avatar.url, "/static/core/science.svg")
        self.assertEquals(entity.name, "Вазомоторные колебания")
        self.assertEquals(entity.description, None)
        self.assertEquals(entity.governor.id, self.__related_user.id)
        self.assertEquals(entity.root_group.id, self.__related_group.id)
        warnings.warn("TO-DO: TestProject.__check_default_fields: check 'permissions' field")
        warnings.warn("TO-DO: TestProject.__check_default_fields: check 'project_apps' field")
        self.assertEquals(entity.project_dir, None)
        self.assertEquals(entity.unix_group, None)

    def _check_default_change(self, entity):
        self.assertEquals(entity.alias, "ontogenesis")
        self.assertEquals(entity.avatar.url, "/static/core/science.svg")
        self.assertEquals(entity.name, "Отногенез")
        self.assertEquals(entity.description,
                          "Исследование критических периодов онтогенеза в первичной зрительной коре")
        self.assertEquals(entity.governor.id, self.__related_user.id)
        self.assertEquals(entity.root_group.id, self.__related_group.id)
        warnings.warn("TO-DO: TestProject.__check_default_fields: check 'permissions' field")
        warnings.warn("TO-DO: TestProject.__check_default_fields: check 'project_apps' field")
        self.assertEquals(entity.project_dir, None)
        self.assertEquals(entity.unix_group, None)

    def _check_reload(self, obj):
        """
        Checks whether the entity is successfully and correctly reloaded.

        :param obj: the entity object within which the entity was reloaded
        :return: nothing
        """
        super()._check_reload(obj)
        self.assertEquals(obj.entity.governor, obj.entity.root_group.governor,
                          "The project leader is not the same to the root group leader")


del BaseTestClass
