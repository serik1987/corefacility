from django.templatetags.static import static
from .entity import Entity
from .entity_fields.field_managers.project_permission_manager import ProjectPermissionManager
from .entity_sets.project_set import ProjectSet
from .entity_fields import EntityField, EntityAliasField, PublicFileManager, ManagedEntityField, ReadOnlyField, \
    RelatedEntityField, EntityContainerManager
from .entity_providers.model_providers.project_provider import ProjectProvider as ModelProvider


class Project(Entity):
    """
    Project is a common operating-system independent workspace that allows several users to work on the same
    data
    """

    _entity_set_class = ProjectSet

    _entity_provider_list = [ModelProvider()]

    _required_fields = ["alias", "name", "root_group"]

    _public_field_description = {
        "alias": EntityAliasField(max_length=64),
        "avatar": ManagedEntityField(PublicFileManager, default=static("core/science.svg"),
                                     description="The project avatar"),
        "name": EntityField(str, min_length=1, max_length=64, description="Project name"),
        "description": EntityField(str, min_length=0, max_length=1024, description="Project description"),
        "governor": ReadOnlyField(description="Project leader"),
        "root_group": RelatedEntityField("core.entity.group.Group",
                                         description="Responsible scientific group"),
        "permissions": ManagedEntityField(ProjectPermissionManager,
                                          description="Permissions of the other users"),
        "project_apps": ManagedEntityField(EntityContainerManager,
                                           description="All applications attached to a certain project"),
        "project_dir": ReadOnlyField(description="Non-public files location directory"),
        "unix_group": ReadOnlyField(description="UNIX group to remote access to project files")
    }

    def __setattr__(self, name, value):
        """
        Sets the public field property.

        If the property name is not within the public or private fields the function throws AttributeError

        :param name: public, protected or private field name
        :param value: the field value to set
        :return: nothing
        """
        super().__setattr__(name, value)
        if name == "root_group":
            self._public_fields["governor"] = value.governor
