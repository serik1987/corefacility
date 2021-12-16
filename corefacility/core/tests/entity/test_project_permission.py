from parameterized import parameterized_class

from core.tests.entity.entity import EntityTest
from core.tests.entity.entity_providers.dump_entity_provider import DumpProjectPermission, DumpProject, DumpUser, \
    DumpGroup


@parameterized_class([
])
class TestProjectPermission(EntityTest):

    _user_list = None
    _group_list = None
    _project_list = None

    def setUp(self):
        super().setUp()
        self._user_list = []
        self._group_list = []
        self._project_list = []

        for login in self.user_data_provider():
            user = self.user_class(login=login)
            user.create()
            self._user_list.append(user)

        for group_name, governor_index, group_user_indices in self.group_data_provider():
            governor = self._user_list[governor_index]
            group = self.group_class(name=group_name, governor=governor)
            group.create()
            self._group_list.append(group)

        for alias, name, root_group_index in self.project_data_provider():
            root_group = self._group_list[root_group_index]
            project = self.project_class(alias=alias, name=name, root_group=root_group)
            project.create()
            self._project_list.append(project)

    def _create_demo_entity(self):
        return self._entity_class()

    def _update_demo_entity(self, entity):
        raise NotImplementedError("TO-DO: self._update_demo_entity")

    def user_data_provider(self):
        return [
            "user1", "user2", "user3", "user4", "user5"
        ]

    def group_data_provider(self):
        return [
            ("Group number 1", 0, [0, 1, 2]),
            ("Group number 2", 2, [1, 2, 3]),
            ("Group number 3", 4, [3, 4])
        ]

    def project_data_provider(self):
        return [
            ("project1", "Project 1", 0),
            ("project2", "Project 2", 0),
            ("project3", "Project 3", 0),
            ("project4", "Project 4", 1),
            ("project5", "Project 5", 2),
        ]


del TestProjectPermission
del EntityTest
