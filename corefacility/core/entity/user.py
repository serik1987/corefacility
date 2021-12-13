from .entity import Entity
from .entity_sets.user_set import UserSet
from .entity_fields import EntityField, EntityAliasField, ManagedEntityField, ReadOnlyField, \
    EntityPasswordManager, PublicFileManager, ExpiryDateManager
from .entity_fields.group_manager import GroupManager
from .entity_exceptions import EntityFieldInvalid


class User(Entity):
    """
    Represents a single user and shall be used for user registration, authorization, authentication and
    modification of access rights
    """

    _entity_set_class = UserSet

    _entity_provider_list = []  # TO-DO: add proper list of all entity providers

    _public_field_description = {
        "login": EntityAliasField(max_length=100),
        "password_hash": ManagedEntityField(EntityPasswordManager,
                                            description="The user password applied during the standard authorization"),
        "name": EntityField(str, max_length=100, description="Name"),
        "surname": EntityField(str, max_length=100, description="Surname"),
        "email": EntityField(str, max_length=254, description="E-mail"),
        "phone": EntityField(str, max_length=20, description="Phone number"),
        "is_locked": EntityField(bool, description="User is locked", default=False),
        "is_superuser": EntityField(bool, description="Is superuser", default=False),
        "is_support": ReadOnlyField(description="Is support", default=False),
        "avatar": ManagedEntityField(PublicFileManager, description="User avatar", default="/path/to/some/file"),
        "unix_group": EntityField(str, max_length=32),
        "home_dir": EntityField(str, max_length=100),
        "activation_code_hash": ManagedEntityField(EntityPasswordManager,
                                                   description="Activation code to be use"),
        "activation_code_expiry_date": ManagedEntityField(ExpiryDateManager,
                                                          description="Activation code expiry date"),
        "groups": ManagedEntityField(GroupManager,
                                     description="List of all groups")
    }

    _required_fields = ["login"]

    def create(self):
        """
        Creates new user

        :return: nothing
        """
        if self._login == "support":
            raise EntityFieldInvalid("You are not allowed to create more 'support' user")
        else:
            super().create()

    def update(self):
        """
        Stores user changes into the external information source

        :return: nothing
        """
        if self._login == "support":
            raise EntityFieldInvalid("You are not allowed to modify the 'support' user")
        else:
            super().update()

    def delete(self):
        """

        :return:
        """
        if self._login == "support":
            raise EntityFieldInvalid("You are not allowed to delete the support user but you can lock it")
        else:
            super().delete()
