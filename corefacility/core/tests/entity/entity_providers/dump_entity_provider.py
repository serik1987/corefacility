from django.core.files import File

from core.entity.entity import Entity
from core.entity.entity_providers.entity_provider import EntityProvider
from core.entity.group import Group
from core.entity.project import Project
from core.entity.user import User


class DumpEntityProvider(EntityProvider):

    _entity_field_cache = None

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
        entity_list = self.get_entity_list(Entity.__class__.__name__)
        entity_info = self.unwrap_entity(entity)
        id = len(entity_list) + 1
        entity._id = id
        entity._wrapped = entity_info

    def update_entity(self, entity: Entity):
        raise NotImplementedError("TO-DO: DumpEntityProvider.update_entity")

    def delete_entity(self, entity: Entity):
        raise NotImplementedError("TO-DO: DumpEntityProvider.delete_entity")

    def wrap_entity(self, external_object):
        raise NotImplementedError("TO-DO: DumpEntityProvider.wrap_entity")

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
        pass

    def attach_entity(self, container: Entity, property_name: str, entity: Entity) -> None:
        pass

    def detach_entity(self, container: Entity, property_name: str, entity: Entity) -> None:
        pass


class DumpProject(Project):

    _entity_provider_list = [DumpEntityProvider()]

    _dump_fields = ["alias", "avatar", "name", "description", "root_group", "project_dir", "unix_group"]


class DumpUser(User):

    _entity_provider_list = [DumpEntityProvider()]

    _dump_fields = ["login", "password_hash", "name", "surname", "email", "phone", "is_locked", "is_superuser",
                    "is_support", "avatar", "unix_group", "home_dir", "activation_code_hash",
                    "activation_code_expiry_date"]


class DumpGroup(Group):

    _entity_provider_list = [DumpEntityProvider()]

    _dump_fields = ["name", "governor"]
