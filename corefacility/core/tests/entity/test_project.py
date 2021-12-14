from parameterized import parameterized_class

from .entity import EntityTest
from .entity_providers.dump_entity_provider import *


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

    def _create_demo_entity(self):
        project = self.entity_name(
            alias="test-project",
            name="The test project",
            description="blah-blah-blah",
            root_group=self.group
        )
        return project

    def _update_demo_entity(self, entity):
        entity.description = "Some useful information appears"


del ProjectTest
del EntityTest
