import os
import shutil

from ...entity import Entity
from ....exceptions.entity_exceptions import BaseDirIoException

from ..entity_provider import EntityProvider


class FilesProvider(EntityProvider):
    """
    This is the base class for all data providers that create, modify and destroy folders
    on creating, modifying or destruction of the entity
    """

    force_disable = False
    """ Disables the provider in force for the testing purpose """

    @property
    def is_provider_on(self):
        """
        True if provider is switched on, False otherwise
        """
        raise NotImplementedError("is_provider_on property")

    @property
    def is_permission_on(self):
        """
        True if permissions set are switched on, False otherwise
        """
        raise NotImplementedError("is_permission_on property")

    def load_entity(self, entity: Entity):
        """
        The method checks that the entity has already been loaded from the database.
        EntityProviders shall use the entity 'id' or '_wrapped' properties of the corresponding
        entity.
        The entity 'id' field is a unique entity number given by the database system. The entity
        id doesn't relate to UID, GID or PID values given to entities by the Unix-like operating
        systems
        :param entity: the entity to load
        :return: the entity value
        """
        if self.is_provider_on:
            dir_name = self.unwrap_entity(entity)
            if os.path.isdir(dir_name):
                return dir_name
            else:
                return None

    def create_entity(self, entity: Entity):
        """
        Creates the entity in a certain entity source and changes the entity's _id and _wrapped properties
        according to how the entity changes its status
        :param entity: The entity to be created on this entity source
        :return: nothing but entity provider must fill necessary entity fields
        """
        if self.is_provider_on:
            dir_name = self.unwrap_entity(entity)
            if self.is_permission_on:
                raise NotImplementedError("Directory create for the real server was still not defined yet.")
            else:
                try:
                    os.mkdir(dir_name)
                except OSError:
                    raise BaseDirIoException()
            self.update_dir_info(entity, dir_name)

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        """
        This function is called when the user tries to save the entity when another duplicated entity
        exists in this entity source.

        The aim of this function is to resolve the underlying conflict and probably call the
        'create_entity' function again
        :param given_entity: the entity the user tries to save
        :param contained_entity: the entity duplicate that has already been present on given entity source
        :return: nothing but must throw an exception when such entity can't be created
        """
        if self.is_provider_on:
            if self.is_permission_on:
                raise NotImplementedError("TO-DO: change proper directory permissions")
            self.update_dir_info(given_entity, contained_entity)

    def change_dir_permissions(self, maker, entity, dir_name):
        raise NotImplementedError("FilesProvider.change_dir_permission is not implemented")

    def update_entity(self, entity: Entity):
        """
        Updates the entity that has been already stored in the database
        :param entity: the entity to be updated
        :return: nothing
        """
        if self.is_provider_on:
            raise NotImplementedError("EntityProvider.update_entity is not implemented")

    def delete_entity(self, entity: Entity):
        """
        Deletes the entity from the external entity source
        :param entity: the entity to be deleted
        :return: nothing
        """
        if self.is_provider_on:
            dir_name = self.unwrap_entity(entity)
            if self.is_permission_on:
                if os.path.isdir(dir_name):
                    raise NotImplementedError("TO-DO: remove the directory for the files provider")
            else:
                if os.path.isdir(dir_name):
                    try:
                        shutil.rmtree(dir_name)
                    except OSError:
                        raise BaseDirIoException()

    def wrap_entity(self, external_object):
        """
        Raises an error since there is no way to recover the entity using the directory
        """
        raise NotImplementedError("EntityProvider.wrap_entity is not implemented")

    def unwrap_entity(self, entity: Entity):
        """
        Returns a full path to the folder corresponding to a particular entity
        :param entity: an entity which folder shall be given
        :return: the folder full path
        """
        if self.is_provider_on:
            raise NotImplementedError("EntityProvider.unwrap_entity is not implemented")

    def update_dir_info(self, entity, dir_name):
        """
        Inserts the directory name to the entity field
        :param entity: the entity to which field the directory name should be inserted
        :param dir_name: full directory path
        :return: nothing
        """
        raise NotImplementedError("FilesProvider.update_dir_info is not implemented")

    def attach_file(self, entity: Entity, name, value) -> None:
        """
        Does nothing because binary data are not processed by this provider
        :param entity: the entity to which the file can be attached
        :param name: the field name to which the file should be attached
        :param value: an instance of django.core.files.File object
        :return: nothing
        """
        pass

    def detach_file(self, entity: Entity, name) -> None:
        """
        Does nothing because binary data are not processed by this provider
        :param entity: the entity from which the file shall be detached
        :param name: the field name from which the file should be detached
        :return: nothing
        """
        pass
