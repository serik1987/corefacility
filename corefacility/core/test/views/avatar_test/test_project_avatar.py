import random

from core.entity.user import UserSet
from core.entity.group import Group
from core.entity.project import Project, ProjectSet

from .avatar_upload_test import AvatarUploadTest


class TestProjectAvatar(AvatarUploadTest):
    """
    Tests whether project avatars were uploaded successfully
    """

    resource_name = "projects"
    """ The URL path segment between the '/api/{version}/' and '/{resource-id}/' parts. """

    entity_set_class = ProjectSet
    """ Class of the entity set to which the avatar shall be attached """

    desired_image_size = (300, 300)
    """ A tuple that contains image width and height respectively """

    resource_id = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        user_set = UserSet()
        for login in ("superuser", "user"):
            user = user_set.get(login)
            group = Group(name=user.name, governor=user)
            group.create()
            project = Project(alias=login, name=user.name, root_group=group)
            project.create()

    def tearDown(self):
        self.resource_id = None
        super().tearDown()

    def get_random_resource_id(self):
        if self.resource_id is None:
            self.resource_id = random.choice(("user", "superuser"))
        return self.resource_id


del AvatarUploadTest
