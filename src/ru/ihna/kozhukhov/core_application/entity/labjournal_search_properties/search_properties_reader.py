from ru.ihna.kozhukhov.core_application.entity.readers.model_reader import ModelReader
from ru.ihna.kozhukhov.core_application.models import LabjournalSearchProperties

from .search_properties_provider import SearchPropertiesProvider
from ...exceptions.entity_exceptions import EntityNotFoundException


class SearchPropertiesReader(ModelReader):
    """
    Reads information about the SearchProperties from the database and returns a list of SearchProperties objects
    """

    _entity_provider = SearchPropertiesProvider()
    """ Provider that must be used to convert SearchProperties instance """

    _category = None
    """ Defines the category filter """

    _user = None
    """ Defines the user filter """

    def __init__(self, category=None, user=None):
        """
        Initializes the model reader

        :param category: the category filter
        :param user: the user filter
        """
        if category is None or user is None:
            raise RuntimeError(
                "To retrieve the SearchProperties instance from the list both category and user filters must be set"
            )
        self._category = category
        self._user = user
        self._entity_data = LabjournalSearchProperties.objects.filter(
            project_id=category.project.id,
            category_id=category.id,
            user_id=user.id,
        )

    def get_only_entity(self):
        """
        Returns the only entity in the list
        """
        external_object = self._entity_data.first()
        if external_object is None:
            raise EntityNotFoundException()
        return external_object
