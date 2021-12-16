from parameterized import parameterized, parameterized_class

from .entity import EntityTest
from .entity_providers.dump_entity_provider import DumpGroup, DumpUser
from ..data_providers.field_value_providers import string_provider


@parameterized_class([
    {
        "entity_name": DumpGroup,
        "user_class": DumpUser
    }
])
class TestGroup(EntityTest):

    main_user = None
    user2 = None
    user3 = None

    def setUp(self):
        super().setUp()
        self.main_user = self.user_class(login="admin")
        self.main_user.create()
        self.user2 = self.user_class(login="user2")
        self.user2.create()
        self.user3 = self.user_class(login="user3")
        self.user3.create()

    @parameterized.expand(string_provider(min_length=1, max_length=256))
    def test_name(self, value, another_value, exc, stage):
        self._test_simple_value_assignment(self._name_init_kwargs(), "name", value, another_value, exc, stage)

    @parameterized.expand([(0,), (1,), (2,), (3,)])
    def test_governor(self, stage):
        self._test_simple_value_assignment(self._governor_init_kwargs(), "governor", self.user3, self.user2,
                                           None, stage)

    def test_forach(self):
        self._test_foreach("name", self.get_sample_group_names())

    def test_slicing(self):
        self._test_slicing("name", self.get_sample_group_names())

    def test_indexing(self):
        self._test_indexing("name", self.get_sample_group_names())

    def get_sample_group_names(self):
        return [
            "Some group number 1",
            "Some group number 2",
            "some group number 3",
            "some group number 4",
            "some group number 5",
            "some group number 6",
            "some group number 7",
            "some group number 8",
            "some group number 9",
            "some group number 10"
        ]

    def _create_demo_entity(self):
        return self.entity_name(
            name="Test group",
            governor=self.main_user
        )

    def _update_demo_entity(self, entity):
        entity.name = "Some other group"

    def _name_init_kwargs(self):
        return {
            "governor": self.main_user
        }

    def _governor_init_kwargs(self):
        return {
            "name": "Other test group"
        }


del TestGroup
del EntityTest
