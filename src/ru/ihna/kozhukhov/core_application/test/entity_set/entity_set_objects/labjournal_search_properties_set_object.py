from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_search_properties import SearchProperties
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType
from .entity_set_object import EntitySetObject


class LabjournalSearchPropertiesSetObject(EntitySetObject):
    """
    A container that temporarily contains the SearchProperties instances for the testing purpose
    """

    _entity_class = SearchProperties
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    _user_set_object = None
    """ Container for the child entities """

    _record_set_object = None
    """ Container for the child entities """

    optical_imaging = None
    """ The first testing project """

    the_rabbit_project = None
    """ The second testing project """

    active_users = None
    """ All active users """

    def __init__(self, user_set_object, record_set_object, _entity_list=None):
        """
        Initializes the container

        :param user_set_object: container that contains various users
        :param record_set_object: container that contains various categories
        :param _entity_list: for service use only
        """
        self._user_set_object = user_set_object
        self._record_set_object = record_set_object
        self.optical_imaging = record_set_object.optical_imaging
        self.the_rabbit_project = record_set_object.the_rabbit_project
        self.active_users = {
            'optical_imaging': {
                'leader': self._user_set_object.get_by_alias('user2'),
                'no_leader': self._user_set_object.get_by_alias('user1'),
            },
            'the_rabbit_project': {
                'leader': self._user_set_object.get_by_alias('user4'),
                'no_leader': self._user_set_object.get_by_alias('user5'),
            }
        }
        if _entity_list is not None:
            super().__init__(_entity_list=_entity_list)
        else:
            self._entities = list()
            for project in self.optical_imaging, self.the_rabbit_project:
                for user_cue in 'leader', 'no_leader':
                    user = self.active_users[project.alias][user_cue]
                    category = RootCategoryRecord(project=project)
                    self._new_properties(category, user)
                    first_level_categories = category.children
                    first_level_categories.record_type = LabjournalRecordType.category
                    first_level_categories.alias = 'a'
                    first_level_category = first_level_categories[0]
                    self._new_properties(first_level_category, user)
                    second_level_categories = first_level_category.children
                    second_level_categories.record_type = LabjournalRecordType.category
                    second_level_category = second_level_categories[0]
                    self._new_properties(second_level_category, user)
                    first_level_categories.alias = 'b'
                    first_level_category = first_level_categories[0]
                    self._new_properties(first_level_category, user)

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(
            self._user_set_object,
            self._record_set_object,
            _entity_list=list(self._entities)
        )

    def filter_by_category(self, category):
        """
        Provides a category filter

        :param category: a category to filter
        """
        self._entities = list(filter(
            lambda search_properties: search_properties.category.id == category.id and \
                search_properties.category.project.id == category.project.id,
            self._entities,
        ))

    def filter_by_user(self, user):
        """
        Provides a user filter

        :param user: a user to filter
        """
        self._entities = list(filter(
            lambda search_properties: search_properties.user.id == user.id,
            self._entities,
        ))

    def _new_properties(self, category, user):
        """
        Adds new properties to the list

        :param category: category where the property set must be saved
        :param user: the user context
        """
        search_properties = SearchProperties(
            category=category,
            user=user,
            properties={
                'category': category.id,
                'user': user.id,
                'alias': category.alias if not category.is_root_record else "root",
                'login': user.login,
            }
        )
        search_properties.create()
        self._entities.append(search_properties)
