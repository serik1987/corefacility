import warnings

from django.core.files.images import ImageFile
from parameterized import parameterized

from core.models import Project as ProjectModel
from core.entity.group import Group
from core.entity.user import User
from core.entity.project import Project
from core.entity.entity_exceptions import EntityDuplicatedException
from core.tests.data_providers.field_value_providers import alias_provider, image_provider, string_provider
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
        super().setUpTestData()
        cls.__related_user = User(login="sergei.kozhukhov")
        cls.__related_user.create()
        cls.__related_group = Group(name="Оптическое картирование", governor=cls.__related_user)
        cls.__related_group.create()
        ProjectObject.define_default_kwarg("root_group", cls.__related_group)

    @parameterized.expand(alias_provider(1, 64))
    def test_alias(self, value, updated_value, exception_to_throw, route_number):
        self._test_field("alias", value, updated_value, exception_to_throw, route_number,
                         use_defaults=False, name="Некий тестовый проект", root_group=self.__related_group)

    def test_alias_uniqueness(self):
        project1 = Project(alias="vasomotor-oscillations", name="Вазомоторные колебания",
                           root_group=self.__related_group)
        project2 = Project(alias="vasomotor-oscillations", name="Стабильность карт",
                           root_group=self.__related_group)
        project1.create()
        with self.assertRaises(EntityDuplicatedException,
                               msg="The project with duplicated alias was successfully created"):
            project2.create()

    @parameterized.expand(image_provider())
    def test_avatar_default(self, image_path, throwing_exception, test_number):
        self._test_file_field("avatar", "/static/core/science.svg", ImageFile,
                              image_path, throwing_exception, test_number)

    @parameterized.expand(string_provider(1, 64))
    def test_name(self, field_value, updated_value, throwing_exception, test_number):
        self._test_field("name", field_value, updated_value, throwing_exception, test_number,
                         use_defaults=False, alias="test", root_group=self.__related_group)

    def test_name_uniqueness(self):
        project1 = Project(alias="alias1", name="Некоторое имя", root_group=self.__related_group)
        project2 = Project(alias="alias2", name="Некоторое имя", root_group=self.__related_group)
        project1.create()
        with self.assertRaises(EntityDuplicatedException,
                               msg="Two projects with the same name were successfully created [Ref. C.1.1.3.4]"):
            project2.create()

    def test_root_group_positive(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        obj.reload_entity()
        self.assertEquals(obj.entity.governor, self.__related_user,
                          "Failed to retrieve the group governor")
        self.assertEquals(obj.entity.root_group, self.__related_group,
                          "Failed to retrieve the root group")

        another_user = User(login="vasily.petrov")
        another_user.create()
        another_group = Group(name="Some another group", governor=another_user)
        another_group.create()
        obj.entity.root_group = another_group
        obj.entity.update()
        self.assertEquals(obj.entity.root_group, another_group,
                          "Attempt to change the project root group had either no or bad effect")
        self.assertEquals(obj.entity.governor, another_user,
                          "The project leader did not change automatically when the project root group was changed")
        obj.reload_entity()
        self.assertEquals(obj.entity.root_group, another_group,
                          "All root group changes were not saved to the database")
        self.assertEquals(obj.entity.governor, another_user,
                          "The project leader was suddenly de-attached when trying to save the root group changes "
                          "to the database")

    def test_root_group_negative(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        another_user = User(login="vasily.petrov")
        with self.assertRaises(ValueError, msg="The user was assigned to the 'root_group' property of the project"):
            obj.entity.root_group = another_user

    def test_root_group_none(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        with self.assertRaises(ValueError, msg="The empty value to the 'root_group' was successfully assigned"):
            obj.entity.root_group = None

    def test_governor_none(self):
        obj = self.get_entity_object_class()()
        obj.create_entity()
        another_user = User(login="vasily.petrov")
        another_user.create()
        with self.assertRaises(ValueError, msg="another value to the 'governor was assigned"):
            obj.entity.governor = another_user

    @parameterized.expand(string_provider(0, 1024))
    def test_description(self, field_value, updated_value, throwing_exception, test_number):
        self._test_field("description", field_value, updated_value, throwing_exception, test_number,
                         use_defaults=True)

    def test_project_dir(self):
        with self.assertRaises(ValueError, msg="the read-only field 'project_dir' has been successfully changed"):
            self.get_entity_object_class()(project_dir="/etc")

    def test_unix_group(self):
        with self.assertRaises(ValueError, msg="The read-only field 'unix_group' has been successfully changed"):
            self.get_entity_object_class()(unix_group="root")

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
