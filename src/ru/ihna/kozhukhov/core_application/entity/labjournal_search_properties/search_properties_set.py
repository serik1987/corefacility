from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.entity.entity_sets.entity_set import EntitySet
from ru.ihna.kozhukhov.core_application.entity.user import User

from ..labjournal_record import CategoryRecord
from .search_properties_reader import SearchPropertiesReader
from ...exceptions.entity_exceptions import EntityNotFoundException


class SearchPropertiesSet(EntitySet):
    """
    Represents a container where different SearchProperties instances were stored.
    """

    _entity_name = _("Individual search parameters")
    """ Human-readable entity name """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_search_properties.SearchProperties"
    """ All entities inside this container must belong to a given class """

    _entity_reader_class = SearchPropertiesReader
    """
    The entity reader is responsible for reading information about the search properties from the database and creating
    the SearchProperties instances base on such a reading
    """

    _entity_filter_list = {
        'category': (CategoryRecord, None),
        'user': (User, None),
    }
    """ List of all filters that can be applied to a given container """

    def get(self, lookup):
        """
        Finds the entity by id or alias
        Entity ID is an entity unique number assigned by the database storage engine during the entity save
        to the database.
        Entity alias is a unique string name assigned by the user during the entity post.

        The function must be executed in one request

        :param lookup: either entity id or entity alias
        :return: the Entity object or DoesNotExist if such entity have not found in the database
        """
        if self.category is None or self.user is None:
            raise RuntimeError("category or user fields are undefined")
        reader = self.entity_reader_class(**self._entity_filters)
        source = reader.get_only_entity()
        provider = reader.get_entity_provider()
        entity = provider.wrap_entity(source)
        entity._category = self.category
        entity._user = self.user
        return entity

    def __getitem__(self, index):
        """
        The EntitySet supports slicing in the following way:
        entity_set[7] returns the 7th entity in the set
        entity_set[3:8] returns from 3rd till 8th entity in the set

        However, the following slicing is not supported:
        - slicing with arbitrary step;
        - slicing where either start or stop index is negative;
        - slicing where start but not stop index is defined.

        The main goal for slicing entity sets is to send SQL queries containing LIMIT clause. Hence, the main
        slice functionality is restricted by condition related to this particular slice. Use the following notation
        to overcome such restriction:

        entity_set[:][3:]

        :param index: either integer or a slice instance
        :return: if index is an integer the method returns a single Entity object. If index is a slice
        the method returns python's list of all found entities (both for 0, 1 and many found entities)
        """
        if self.category is None or self.user is None:
            raise RuntimeError("category or user fields are undefined")
        reader = self.entity_reader_class(**self._entity_filters)
        provider = reader.get_entity_provider()
        if isinstance(index, slice) and 0 not in range(index.stop)[index]:
            raise EntityNotFoundException()
        if isinstance(index, int) and index != 0:
            raise EntityNotFoundException()
        entity = provider.wrap_entity(reader[0])
        entity._category = self.category
        entity._user = self.user
        return entity

    def __iter__(self):
        """
        The EntitySet supports iteration that allows to sequentially process each entity from the set
        """
        reader = self.entity_reader_class(**self._entity_filters)
        provider = reader.get_entity_provider()
        for external_object in reader:
            entity = provider.wrap_entity(external_object)
            entity._category = self.category
            entity._user = self.user
            yield entity

