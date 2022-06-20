from django.templatetags.static import static
from django.db import transaction

from .arbitrary_access_level_entity import ArbitraryAccessLevelEntity
from .entity_fields.field_managers.project_permission_manager import ProjectPermissionManager
from .entity_sets.project_set import ProjectSet
from .entity_fields import EntityField, EntityAliasField, PublicFileManager, ManagedEntityField, ReadOnlyField, \
    RelatedEntityField, ProjectApplicationManager
from .entity_providers.model_providers.project_provider import ProjectProvider as ModelProvider


class Project(ArbitraryAccessLevelEntity):
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
        "project_apps": ManagedEntityField(ProjectApplicationManager,
                                           description="All applications attached to a certain project"),
        "project_dir": ReadOnlyField(description="Non-public files location directory"),
        "unix_group": ReadOnlyField(description="UNIX group to remote access to project files"),

        "user_access_level": ReadOnlyField(description="The user access level list (if applicable)"),
        "is_user_governor": ReadOnlyField(
            description="Whether the user is governor for group with 'full' access (if applicable)")
    }

    @classmethod
    def get_access_level_hierarchy(cls):
        """
        Returns a dictionary containing access levels and their weights. If the user has two different access
        levels to the same entity, this feature will select a level with the highest weight.

        :return: a dictionary which keys are access level aliases and which values are access level weights
        """
        return {
            "no_access": 0.0,
            "data_view": 1.0,
            "data_process": 2.0,
            "data_add": 3.0,
            "data_full": 4.0,
            "full": 5.0,
        }

    def force_delete(self):
        """
        Deletes the project with all its dependent instances

        :return: nothing
        """
        with transaction.atomic():
            self.delete()

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

    def __eq__(self, other):
        """
        Compares two projects (to be used for the debugging purpose)

        :param other: the other project to compare to
        :return: nothing
        """
        if not isinstance(other, Project):
            return False
        if self.id != other.id:
            return False
        if self.alias != other.alias:
            return False
        if self.name != other.name:
            return False
        if self.description != other.description:
            return False
        if self.root_group != other.root_group:
            return False
        return True
