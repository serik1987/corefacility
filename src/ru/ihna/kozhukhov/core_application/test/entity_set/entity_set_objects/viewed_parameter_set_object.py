from ru.ihna.kozhukhov.core_application.entity.labjournal_viewed_parameter import ViewedParameter
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityNotFoundException
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType

from .entity_set_object import EntitySetObject


class ViewedParameterSetObject(EntitySetObject):
    """
    Manages the list of viewed parameter for the testing purpose
    """

    _user_set_object = None
    """ Entity set object for children """

    _record_set_object = None
    """ Entity set object for children """

    _parameter_descriptor_object = None
    """ Entity set object for children """

    active_users = None
    """ Users that fill their columns """

    _entity_class = ViewedParameter
    """ Defines the entity class. The EntitySetObject will create entities belonging exactly to this class. """

    def __init__(self, user_set_object, record_set_object, parameter_descriptor_object, _entity_list=None):
        """
        Initializes a set of certain custom entity objects and adds such objects to the database.
        Values of the object fields shall be returned by the data_provider function.

        :param user_set_object: user that shall be used to make a user context
        :param record_set_object: all labjournal records where viewed parameters will be created
        :param parameter_descriptor_object: all descriptors that will be wrapped by the viewed parameters
        :param _entities: This is an internal argument. Don't use it.
        """
        self._user_set_object = user_set_object
        self._record_set_object = record_set_object
        self._parameter_descriptor_object = parameter_descriptor_object
        if _entity_list is not None:
            super().__init__(_entity_list=_entity_list)
        else:
            self._entities = list()
            self.active_users = {
                'optical_imaging': {
                    'leader': self._user_set_object.get_by_alias('user2'),
                    'no_leader': self._user_set_object.get_by_alias('user1'),
                },
                'the_rabbit_project': {
                    'leader': self._user_set_object.get_by_alias('user4'),
                    'no_leader': self._user_set_object.get_by_alias('user3')
                }
            }
            for parameter_descriptor in self._parameter_descriptor_object.entities:
                category_list = [parameter_descriptor.category]
                child_categories = parameter_descriptor.category.children
                child_categories.record_type = LabjournalRecordType.category
                try:
                    category_list.append(child_categories[1])
                except EntityNotFoundException:
                    pass
                if hasattr(parameter_descriptor.category, 'parent_category'):
                    category_list.append(parameter_descriptor.category.parent_category)
                for category in category_list:
                    self._add_viewed_parameters_for_descriptor(parameter_descriptor, category, 'leader')
                    self._add_viewed_parameters_for_descriptor(parameter_descriptor, category, 'no_leader')

    def _add_viewed_parameters_for_descriptor(self, parameter_descriptor, category, login):
        """
        Adds viewed parameter for a given descriptor

        :param parameter_descriptor: a descriptor for which the parameters shall be added
        :param category: a category where the parameter shall be formed
        :param login: login of a user that shall be used for context
        """
        viewed_parameter = ViewedParameter(
            descriptor=parameter_descriptor,
            category=category,
            user=self.active_users[parameter_descriptor.category.project.alias][login]
        )
        viewed_parameter.create()
        self._entities.append(viewed_parameter)

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        viewed_parameter_set_object = ViewedParameterSetObject(
            self._user_set_object,
            self._record_set_object,
            self._parameter_descriptor_object,
            _entity_list=list(self._entities)
        )
        viewed_parameter_set_object.active_users = self.active_users
        return viewed_parameter_set_object

    def sort(self):
        """
        Provides default sort for the viewed parameters
        """
        self._entities = list(sorted(self._entities, key=lambda entity: entity.index))

    def filter_by_category(self, category):
        """
        Applies the category filter

        :param category: show only viewed parameters that belong to a given category
        """
        self._entities = list(filter(
            lambda viewed_parameter: viewed_parameter.category.id == category.id and \
                                     viewed_parameter.category.project.id == category.project.id,
            self._entities
        ))

    def filter_by_user(self, user):
        """
        Applies the user filter

        :param user: show only viewed parameters that were added by a given user
        """
        self._entities = list(filter(
            lambda viewed_parameter: viewed_parameter.user.id == user.id,
            self._entities
        ))
