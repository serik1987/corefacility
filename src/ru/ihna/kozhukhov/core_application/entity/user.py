from django.templatetags.static import static
from django.db import transaction

from .. import App

from .entity import Entity
from .entity_sets.user_set import UserSet
from .fields import EntityField, EntityAliasField, ManagedEntityField, ReadOnlyField, \
    BooleanField, BooleanReadOnlyField
from .field_managers.entity_password_manager import EntityPasswordManager
from .field_managers.public_file_manager import PublicFileManager
from .field_managers.expiry_date_manager import ExpiryDateManager
from .field_managers.group_manager import GroupManager
from ..exceptions.entity_exceptions import EntityFieldInvalid, SupportUserModificationNotAllowed
from .providers.model_providers.user_provider import UserProvider as ModelProvider
from .providers.posix_providers.user_provider import UserProvider as PosixProvider
from .providers.file_providers.user_files_provider import UserFilesProvider


class User(Entity):
    """
    Represents a single user and shall be used for user registration, authorization, authentication and
    modification of access rights
    """

    is_authenticated = False
    """ This tag is added just for compatibility with REST Framework authenticators. This is absolutely useless.  """

    _entity_set_class = UserSet

    _entity_provider_list = [UserFilesProvider(), ModelProvider(), PosixProvider()]

    _public_field_description = {
        "login": EntityAliasField(max_length=100),
        "password_hash": ManagedEntityField(EntityPasswordManager,
                                            description="The user password applied during the standard authorization"),
        "name": EntityField(str, max_length=100, description="Name"),
        "surname": EntityField(str, max_length=100, description="Surname"),
        "email": EntityField(str, max_length=254, description="E-mail"),
        "phone": EntityField(str, max_length=20, description="Phone number"),
        "is_locked": BooleanField(description="User is locked", default=False),
        "is_superuser": BooleanField(description="Is superuser", default=False),
        "is_support": BooleanReadOnlyField(description="Is support", default=False),
        "avatar": ManagedEntityField(PublicFileManager,
                                     description="User avatar",
                                     default=static("ru.ihna.kozhukhov.core_application/user.svg"),
                                     ),
        "unix_group": ReadOnlyField(description="UNIX group"),
        "home_dir": ReadOnlyField(description="Home directory"),
        "activation_code_hash": ManagedEntityField(EntityPasswordManager,
                                                   description="Activation code to be use"),
        "activation_code_expiry_date": ManagedEntityField(ExpiryDateManager,
                                                          description="Activation code expiry date"),
        "groups": ManagedEntityField(GroupManager,
                                     description="List of all groups")
    }

    _required_fields = ["login"]

    @property
    def pk(self):
        """
        This property is added for compatibility with REST framework throttling facilities

        :return: user ID
        """
        return self.id

    def create(self):
        """
        Creates new user

        :return: nothing
        """
        if self._login == "support":
            raise SupportUserModificationNotAllowed()
        else:
            super().create()

    def update(self):
        """
        Stores user changes into the external information source

        :return: nothing
        """
        if self._login == "support" and self._edited_fields != {"is_locked"}:
            raise SupportUserModificationNotAllowed()
        else:
            super().update()

    def force_delete(self):
        """
        Deletes the user together with all group where the user is root and together with
        all projects where the user is governor

        :return: nothing
        """
        with self._get_transaction_mechanism():
            for group in self.groups:
                if group.governor.id == self.id:
                    group.log = self.log
                    group.force_delete()
            self.delete()

    def delete(self):
        """
        Deletes the user

        :return:
        """
        if self._login == "support":
            raise EntityFieldInvalid("You are not allowed to delete the support user but you can lock it")
        else:
            super().delete()

    def __eq__(self, other):
        """
        Compares two users

        :param other: the user to compare
        :return: True if two users are the same. False for otherwise
        """
        if not isinstance(other, User):
            return False
        if self.id != other.id:
            return False
        if self.login != other.login:
            return False
        if self.name != other.name:
            return False
        if self.surname != other.surname:
            return False
        if self.email != other.email:
            return False
        if self.avatar != other.avatar:
            return False
        return True

    def __lt__(self, other):
        """
        Declares conditions under which one user is less than another one.
        This is important for manual user sorting by means of Python facilities.

        :return: True if this object is less than the other object, False otherwise
        """
        if not isinstance(other, User):
            raise NotImplemented("Two values were incomparable")
        if self.surname < other.surname:
            return True
        elif self.surname > other.surname:
            return False
        elif self.name < other.name:
            return True
        elif self.name > other.name:
            return False
        elif self.login < other.login:
            return True
        else:
            return False

    def _get_transaction_mechanism(self):
        return transaction.atomic()

    def generate_password(self):
        symbol_alphabet = EntityPasswordManager.SMALL_LATIN_LETTERS + EntityPasswordManager.DIGITS + \
            EntityPasswordManager.BIG_LATIN_LETTERS
        max_symbols = App().get_max_password_symbols()
        new_password = self.password_hash.generate(symbol_alphabet, max_symbols)
        return new_password
