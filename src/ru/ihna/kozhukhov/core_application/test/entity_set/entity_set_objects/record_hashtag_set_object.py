from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import RecordHashtag

from .entity_set_object import EntitySetObject


class RecordHashtagSetObject(EntitySetObject):
    """
    Creates environment for the testing the record hashtags
    """

    _record_set_object = None
    """ Container where all child entities contained """

    _entity_class = RecordHashtag
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    _alias_field = 'description'
    """ The field that is used as string ID """

    def __init__(self, record_set_object, _entity_list = None):
        """
        Initializes the hashtag set object

        :param record_set_object: container where sample projects and records contained
        :param _entity_list: for service use only
        """
        self._record_set_object = record_set_object
        super().__init__(_entity_list=_entity_list)
        if _entity_list is None:  # if no cloning
            records = list(filter(
                lambda record: record.level == 2 and record.project.id == self._record_set_object.optical_imaging.id,
                self._record_set_object.entities
            ))
            hashtag1 = self.get_by_alias("шахматный")
            hashtag2 = self.get_by_alias("редкий")
            hashtag3 = self.get_by_alias("редчайший")
            [record.hashtags.add([hashtag1.id]) for record in records[::2]]
            [record.hashtags.add([hashtag2.id]) for record in records[::3]]
            [record.hashtags.add([hashtag3.id]) for record in records[::4]]

    def data_provider(self):
        """
        Defines properties of custom entity objects created in the constructor.

        :return: list of field_name => field_value dictionary reflecting properties of a certain user
        """
        entity_data = list()
        for project in self._record_set_object.optical_imaging, self._record_set_object.the_rabbit_project:
            entity_data.append(dict(
                description="шахматный",
                project=project,
            ))
            entity_data.append(dict(
                description="редкий",
                project=project,
            ))
            entity_data.append(dict(
                description="редчайший",
                project=project,
            ))
        return entity_data

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._record_set_object, _entity_list=list(self._entities))

    def sort(self):
        """
        Sorts the entities inside this temporary container
        """
        self._entities = list(sorted(
            self._entities, key=lambda hashtag: hashtag.description
        ))

    def filter_by_project(self, project):
        """
        Filters only such records that belong to a given project

        :param project: the project to filter
        """
        self._entities = list(filter(
            lambda hashtag: hashtag.project.id == project.id,
            self._entities,
        ))

    def filter_by_type(self, hashtag_type):
        """
        Filters only such records that belong to a given type

        :param hashtag_type: the hashtag type to filter
        """
        self._entities = list(filter(
            lambda hashtag: hashtag.type == hashtag_type,
            self._entities,
        ))

    def filter_by_description(self, description):
        """
        Filters only such records which description starts from a given line

        :param description: a substring to search
        """
        self._entities = list(filter(
            lambda hashtag: hashtag.description.startswith(description),
            self._entities,
        ))
