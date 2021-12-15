import sys

from django.core.files import File
from django.utils.module_loading import import_string

from core.entity.entity import Entity
from core.entity.entity_exceptions import EntityNotFoundException
from core.entity.entity_providers.entity_provider import EntityProvider
from core.entity.entity_readers.entity_reader import EntityReader
from core.entity.entity_sets.project_set import ProjectSet
from core.entity.entity_sets.user_set import UserSet
from core.entity.group import Group
from core.entity.project import Project
from core.entity.user import User


class DumpEntityProvider(EntityProvider):

    _entity_field_cache = None

    _class_name = None

    @classmethod
    def clear_entity_field_cache(cls):
        cls._entity_field_cache = dict()

    @classmethod
    def get_entity_list(cls, entity_class):
        if entity_class in cls._entity_field_cache:
            entity_list = cls._entity_field_cache[entity_class]
        else:
            entity_list = list()
            cls._entity_field_cache[entity_class] = entity_list
        return entity_list

    @classmethod
    def init_entity_class(cls, class_name):
        if class_name not in cls._entity_field_cache:
            cls._entity_field_cache[class_name] = list()

    def load_entity(self, entity: Entity):
        if entity.id is not None or entity._wrapped is not None:
            return entity
        entity_class = entity.__class__.__name__
        entity_list = self.get_entity_list(entity_class)
        try:
            entity_alias = entity._alias
        except AttributeError:
            return None
        else:
            for entity_info in entity_list:
                if entity_alias == entity_info['alias']:
                    another_entity = self.wrap_entity(entity_info)
                    return another_entity
            return None

    def resolve_conflict(self, given_entity: Entity, contained_entity: Entity):
        raise NotImplementedError("TO-DO: DumpEntityProvider.resolve_conflict")

    def create_entity(self, entity: Entity):
        entity_list = self.get_entity_list(entity.__class__.__name__)
        entity_info = self.unwrap_entity(entity)
        id = len(entity_list) + 1
        entity._id = id
        entity._wrapped = entity_info
        entity_list.append(entity_info)

    def update_entity(self, entity: Entity):
        entity_info = entity._wrapped
        for field_name in entity._edited_fields:
            entity_info[field_name] = getattr(entity, "_" + field_name)

    def delete_entity(self, entity: Entity):
        entity_list = self.get_entity_list(entity.__class__.__name__)
        index = entity.id - 1
        del entity_list[index]

    def wrap_entity(self, external_object):
        entity_list = self.get_entity_list(self._class_name)
        kwargs = external_object.copy()
        kwargs["_src"] = external_object
        i = 0
        for obj in entity_list:
            if obj == external_object:
                kwargs['id'] = i+1
                break
            i += 1
        module = sys.modules[__name__]
        entity_class = getattr(module, str(self._class_name))
        return entity_class(**kwargs)

    def unwrap_entity(self, entity: Entity):
        if entity._wrapped is None:
            entity_info = dict()
        else:
            entity_info = entity._wrapped
        for field in entity._dump_fields:
            entity_info[field] = getattr(entity, '_' + field)
        return entity_info

    def attach_file(self, name: str, value: File) -> None:
        raise NotImplementedError("TO-DO: DumpEntityProvider.attach_file")

    def detach_file(self, name: str) -> None:
        raise NotImplementedError("TO-DO: DumpEntityProvider.detach_file")

    def attach_entity(self, container: Entity, property_name: str, entity: Entity) -> None:
        raise NotImplementedError("TO-DO: DumpEntityProvider.attach_entity")

    def detach_entity(self, container: Entity, property_name: str, entity: Entity) -> None:
        raise NotImplementedError("TO-DO: DumpEntityProvider.detach_entity")


class DumpEntityReader(EntityReader):

    _class_name = None

    @classmethod
    def get_entity_provider(cls):
        provider = DumpEntityProvider()
        provider._class_name = cls._class_name
        return provider

    def __init__(self, **kwargs):
        self.__entity_list = DumpEntityProvider.get_entity_list(self._class_name)

    def __iter__(self):
        provider = self.get_entity_provider()
        entity_list = provider.get_entity_list(self._class_name)
        for entity_info in entity_list:
            yield entity_info

    def __getitem__(self, index):
        provider = self.get_entity_provider()
        entity_list = provider.get_entity_list(self._class_name)
        return entity_list[index]

    def get(self, **kwargs):
        if "id" in kwargs:
            id = kwargs['id']
            try:
                return self.__entity_list[id-1]
            except IndexError:
                raise EntityNotFoundException()
        elif "alias" in kwargs:
            alias = kwargs['alias']
            for source in self.__entity_list:
                if 'alias' in source and source['alias'] == alias:
                    return source
            raise EntityNotFoundException()
        else:
            raise EntityNotFoundException()


class DumpProjectEntityReader(DumpEntityReader):

    _class_name = "DumpProject"


class DumpProjectSet(ProjectSet):

    _entity_class = "DumpProject"

    _entity_reader_class = DumpProjectEntityReader


class DumpProject(Project):

    _entity_set_class = DumpProjectSet

    _entity_provider_list = [DumpEntityProvider()]

    _dump_fields = ["alias", "avatar", "name", "description", "root_group", "project_dir", "unix_group"]


class DumpUserEntityReader(DumpEntityReader):

    _class_name = "DumpUser"


class DumpUserSet(UserSet):

    _entity_class = "DumpUser"

    _entity_reader_class = DumpUserEntityReader


class DumpUser(User):

    _entity_provider_list = [DumpEntityProvider()]

    _entity_set_class = DumpUserSet

    _dump_fields = ["login", "password_hash", "name", "surname", "email", "phone", "is_locked", "is_superuser",
                    "is_support", "avatar", "unix_group", "home_dir", "activation_code_hash",
                    "activation_code_expiry_date"]


class DumpGroup(Group):

    _entity_provider_list = [DumpEntityProvider()]

    _dump_fields = ["name", "governor"]
