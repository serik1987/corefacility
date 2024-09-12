from ru.ihna.kozhukhov.core_application.entity.entity import Entity
from ru.ihna.kozhukhov.core_application.entity.field_managers.entity_value_manager import EntityValueManager
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityOperationNotPermitted, \
    EntityNotFoundException


class HashtagEntityManager(EntityValueManager):
    """
    Manages list of different entities this hashtag is attached
    """

    _entity_table = None
    """ A database table where all entities are stored """

    _association_table = None
    """
    A database table that stores connections between entities and their hashtags
    Such table shall have two columns. The first column is named 'hashtag_id' and contains IDs of connected hashtags.
    The second column contains IDs of entities that are connected to given hashtags
    """

    _entity_field = None
    """ Name of a column in the association table where entity IDs are stored  """

    def add(self, entity_list):
        """
        Adds the hashtag to given entities

        :param entity_list: list of entities which this hashtag should be added to (each item is either Entity instance
            or an integer reflecting the record ID)
        """
        self._check_hashtag_state()
        entity_list = self._get_entity_ids(entity_list)
        existent_entity_list = self._get_existent_entity_ids(entity_list)
        entities_to_add = entity_list - existent_entity_list
        self._check_entities_exist(entities_to_add)
        # Let's remain some debugging line below
        # print(self.__class__, entities_to_add)
        association_models = [
            self._association_table(**{
                'hashtag_id': self._entity.id,
                self._entity_field: entity_id
            })
            for entity_id in entities_to_add
        ]
        self._association_table.objects.bulk_create(association_models)

    def remove(self, entity_list):
        """
        Removes the hashtag from given entities

        :param entity_list: list of entities which this hashtag should be added to (each item is either Entity instance
            or an integer reflecting the record ID)
        """
        self._check_hashtag_state()
        entity_list = self._get_entity_ids(entity_list)
        self._get_existent_entity_lookup_queryset(entity_list).delete()

    def _check_hashtag_state(self):
        """
        Throws an exception when the hashtag is in 'creating' or 'deleted' state. (Adding such a hashtag to entities
        is not possible)
        """
        if self._entity.state == 'creating' or self._entity.state == 'deleted':
            raise EntityOperationNotPermitted("This operation is not permitted because the hashtag is in bad state")

    def _get_entity_ids(self, entity_list):
        """
        Transforms the entity list given as input to the add() and remove() method to the set of IDs of desired entities

        :param entity_list: list of entities which this hashtag should be added to (each item is either Entity instance
            or an integer reflecting the record ID)
        :return: set of IDs of entities to add or remove
        """
        entity_ids = {entity.id if isinstance(entity, Entity) else entity for entity in entity_list}
        if None in entity_ids:  # It happens when the entity is in 'creating' or 'deleted' state
            raise EntityNotFoundException()
        return entity_ids

    def _get_existent_entity_ids(self, entity_ids):
        """
        Returns IDs of those entities that:
        (a) are mentioned as input arguments to add() and remove() methods;
        (b) hashtag is added to them.

        :param entity_ids: IDs of all entities included in the input argument
        :return: IDs of only those entities which a given hashtag has been already added to
        """
        existent_entity_queryset = self._get_existent_entity_lookup_queryset(entity_ids) \
            .values_list(self._entity_field)
        existent_entity_list = {entity_id for (entity_id,) in existent_entity_queryset}
        return existent_entity_list

    def _get_existent_entity_lookup_queryset(self, entity_ids):
        """
        Returns a queryset that allows to look to deal with all associations between a given hashtag and all entities
        that: (a) are mentioned as input arguments to add() and remove() methods; (b) hashtag is added to them.

        :param entity_ids: IDs of all entities included in the input argument
        :return: the QuerySet object
        """
        return self._association_table.objects \
            .filter(**{
                self._entity_field + "__in": entity_ids,
                'hashtag_id': self._entity.id,
            })

    def _check_entities_exist(self, entity_ids):
        """
        Check that all entities within the given entity list exists. If at least one entity doesn't exist
        EntityDuplicatedException will be thrown

        :param entity_ids: a set of IDs of entities which are required to check.
        """
        created_entities_to_add = len(self._entity_table.objects.filter(
            pk__in=entity_ids,
            project_id=self._entity.project.id,
        ))
        if created_entities_to_add != len(entity_ids):
            raise EntityNotFoundException()
