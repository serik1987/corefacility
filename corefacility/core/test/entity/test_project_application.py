from django.test import TestCase

from core.entity.project_application import ProjectApplication, ProjectApplicationSet
from core.entity.project import Project
from core.entity.user import User
from core.entity.group import Group
from imaging import App as ImagingApp


class TestProjectApplication(TestCase):
    """
    Provides testing routines for the ProjectApplication entity
    """

    _sample_user = None
    _sample_group = None
    _sample_project = None

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

    def test_sample(self):
        project_app = ProjectApplication(application=ImagingApp(), project=self._sample_project, is_enabled=True)
        project_app.create()
        project_app.is_enabled = False
        project_app.update()
        project_app_id = project_app.id
        del project_app
        project_app_set = ProjectApplicationSet()
        project_app = project_app_set.get(project_app_id)
        project_app.is_enabled = True
        project_app.delete()
        print("Manual entity test completed")
