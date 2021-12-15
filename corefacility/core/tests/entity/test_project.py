from parameterized import parameterized_class, parameterized

from .entity import EntityTest
from .entity_providers.dump_entity_provider import *
from core.tests.data_providers.field_value_providers import alias_provider, string_provider


def project_aliases_provider():
    return [[["project1", "project2", "project3", "project4", "project5", "project6",
             "project7", "project8", "project9", "project10"]]]


@parameterized_class([
    {
        "entity_name": DumpProject,
        "related_user": DumpUser,
        "related_group": DumpGroup,
    }
])
class ProjectTest(EntityTest):
    user = None
    group = None

    def setUp(self):
        DumpEntityProvider.clear_entity_field_cache()
        self.user = self.related_user(login="test123")
        self.user.create()
        self.group = self.related_group(name="Test group", governor=self.user)
        self.group.create()

    def _alias_init_kwargs(self):
        return {
            "name": "The test project",
            "root_group": self.group
        }

    def _name_init_kwargs(self):
        return {
            "alias": "test-project",
            "root_group": self.group
        }

    def _description_init_kwargs(self):
        return {
            "alias": "test",
            "name": "The Test",
            "root_group": self.group,
        }

    def test_empty_alias(self):
        self._test_for_empty(self._alias_init_kwargs(), "alias")

    @parameterized.expand(alias_provider(min_length=1, max_length=64))
    def test_alias(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._alias_init_kwargs(), "alias", value, initial_value, exc, stage)

    def test_load_default_file(self):
        self._test_load_default_file("avatar")

    @parameterized.expand(string_provider(min_length=1, max_length=64))
    def test_name(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._name_init_kwargs(), "name", value, initial_value, exc, stage)

    @parameterized.expand(string_provider(min_length=None, max_length=1024))
    def test_description(self, value, initial_value, exc, stage):
        self._test_simple_value_assignment(self._description_init_kwargs(), "description", value, initial_value,
                                           exc, stage)

    def test_root_group(self):
        entity = self._create_demo_entity()
        entity.create()
        entity_id = entity.id
        del entity

        entity = self.entity_name.get_entity_set_class()().get(entity_id)
        self.assertEquals(entity.root_group.id, self.group.id, msg="The project root group was not properly attached")
        self.assertEquals(entity.root_group.name, self.group.name,
                          msg="The root group name was not loaded when loading the project itself")

        group2 = self.related_group(name="Some other group", governor=self.user)
        with self.assertRaises(ValueError,
                               msg="The root group not being saved to the database is correctly assigned"):
            entity.root_group = group2
        group2.create()
        entity.root_group = group2
        entity.update()
        del entity

        entity = self.entity_name.get_entity_set_class()().get(entity_id)
        self.assertEquals(entity.root_group.id, group2.id,
                          msg="Unable to change the project's root group when project is loaded")

    def test_governor(self):
        self._test_read_only_field("governor")

    def test_permissions(self):
        self._test_read_only_field("permissions")

    def test_project_apps(self):
        self._test_read_only_field("project_apps")

    def test_project_dir(self):
        self._test_read_only_field("project_dir")

    def test_unix_group(self):
        self._test_read_only_field("unix_group")

    @parameterized.expand(project_aliases_provider())
    def test_foreach(self, aliases):
        self._test_foreach("alias", aliases)

    @parameterized.expand(project_aliases_provider())
    def test_slicing(self, aliases):
        self._test_slicing("alias", aliases)

    @parameterized.expand(project_aliases_provider())
    def test_indexing(self, aliases):
        self._test_indexing("alias", aliases)

    @parameterized.expand(project_aliases_provider())
    def test_looking_for_alias(self, aliases):
        self._create_several_entities("alias", aliases)
        entity_set = self.entity_name.get_entity_set_class()()
        for alias in aliases:
            entity = entity_set.get(alias)
            self.assertEquals(entity.alias, alias,
                              "The project with alias '%s' was not found" % alias)

    def _create_demo_entity(self):
        project = self.entity_name(**self._description_init_kwargs())
        return project

    def _update_demo_entity(self, entity):
        entity.description = "Some useful information appears"


del ProjectTest
del EntityTest
