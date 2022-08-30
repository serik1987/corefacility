from parameterized import parameterized

from core.authorizations.standard import StandardAuthorization
from core.entity.project_application import ProjectApplication
from core.entity.project import Project
from core.entity.user import User
from core.entity.group import Group
from imaging import App as ImagingApp
from roi import App as RoiApp

from core.test.data_providers.field_value_providers import boolean_provider, put_stages_in_provider
from .base_test_class import BaseTestClass
from .entity_objects.project_application_object import ProjectApplicationObject
from ...entity.entity_exceptions import EntityDuplicatedException


def application_project_provider():
    return put_stages_in_provider([
        ("valid_project", 0, 1, None),
        ("not_a_project", 2, 1, ValueError),
        ("None_value", 3, 1, ValueError),
        ("not_created_project", 4, 1, ValueError),
    ])


def application_provider():
    return put_stages_in_provider([
        ("positive", False, ImagingApp, RoiApp, None),
        ("not_an_app", False, StandardAuthorization, RoiApp, ValueError),
        ("not_a_module", False, "proj", RoiApp, ValueError),
        ("uninstalled_app", True, RoiApp, ImagingApp, ValueError),
        ("none_app", False, ImagingApp, RoiApp, None),
    ])


class TestProjectApplication(BaseTestClass):
    """
    Provides testing routines for the ProjectApplication entity
    """

    _entity_object_class = ProjectApplicationObject
    """ The entity object class. New entity object will be created from this class """

    _sample_user = None
    _sample_group = None
    _sample_project = None
    _another_project = None
    _project_values = None
    _creating_project = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._sample_user = User(login="sergei.kozhukhov")
        cls._sample_user.create()
        cls._sample_group = Group(name="Оптическое картирование", governor=cls._sample_user)
        cls._sample_group.create()
        cls._sample_project = Project(alias="vasomotor-oscillations", name="Вазомоторные колебания",
                                      root_group=cls._sample_group)
        cls._sample_project.create()
        ProjectApplicationObject.define_default_kwarg("project", cls._sample_project)
        cls._another_project = Project(alias="ontogenesis", name="Онтогенез", root_group=cls._sample_group)
        cls._another_project.create()
        cls._creating_project = Project(alias="eeg", name="ЭЭГ", root_group=cls._sample_group)
        cls._project_values = (cls._sample_project, cls._another_project, ImagingApp(), None, cls._creating_project)

    @parameterized.expand(boolean_provider())
    def test_is_enabled(self, *args):
        self._test_field("is_enabled", *args, use_defaults=False,
                         application=ImagingApp(), project=self._sample_project)

    @parameterized.expand(application_project_provider())
    def test_project(self, test_name, field_value, updated_value, exception_to_throw, route_number):
        field_value = self._project_values[field_value]
        updated_value = self._project_values[updated_value]
        self._test_field("project", field_value, updated_value, exception_to_throw, route_number, use_defaults=False,
                         application=ImagingApp(), is_enabled=True)

    @parameterized.expand(application_provider())
    def test_application(self, test_name, shall_uninstall_app, initial_app_class, changed_app_class, exception_to_throw,
                         route_number):
        if isinstance(initial_app_class, str):
            initial_app = self._sample_project
        else:
            initial_app = initial_app_class()
        if shall_uninstall_app:
            initial_app.delete()
        changed_app = changed_app_class()
        self._test_field("application", initial_app, changed_app, exception_to_throw, route_number,
                         use_defaults=False, project=self._another_project, is_enabled=True)

    def test_double_create(self):
        p1 = ProjectApplication(project=self._sample_project, application=ImagingApp(), is_enabled=True)
        p1.create()
        p2 = ProjectApplication(project=self._sample_project, application=ImagingApp(), is_enabled=False)
        with self.assertRaises(EntityDuplicatedException,
                               msg="Each ProjectApplication entity is a unique pair (project, application)"):
            p2.create()

    def _check_default_fields(self, project_application):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param project_application: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertTrue(project_application.is_enabled, "The is_enabled property must be transmitted correctly")
        self._check_non_changed_fields(project_application)

    def _check_default_change(self, project_application):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param project_application: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertFalse(project_application.is_enabled, "The is_enabled property must be changed correctly")
        self._check_non_changed_fields(project_application)

    def _check_non_changed_fields(self, project_application):
        self.assertEquals(project_application.project.alias, "vasomotor-oscillations",
                          "The project alias must be transmitted correctly")
        self.assertEquals(project_application.project.name, "Вазомоторные колебания",
                          "The project name must be transmitted correctly")
        self.assertEquals(project_application.project.root_group.id, self._sample_group.id,
                          "The project root group must be retrieved correctly")

        self.assertIsInstance(project_application.application, ImagingApp,
                              "The project application must be properly retrieved")
        self.assertEquals(project_application.application.state, "loaded",
                          "The project application must be autoloaded when loading the ProjectApplication instance")


del BaseTestClass
