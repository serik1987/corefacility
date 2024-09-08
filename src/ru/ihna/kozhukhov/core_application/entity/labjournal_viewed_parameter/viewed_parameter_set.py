from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.models import LabjournalParameterView

from ..entity_sets.swappable_entity_set import SwappableEntitySet
from ..labjournal_record.category_record import CategoryRecord
from ..user import User
from .viewed_parameter_reader import ViewedParameterReader


class ViewedParameterSet(SwappableEntitySet):
    """
    Represents a container that holds all viewed parameters that belong to a given category
    """

    _entity_name = _("Viewed Parameter")
    """ Human-readable entity name """

    _entity_class = "ru.ihna.kozhukhov.core_application.entity.labjournal_viewed_parameter.ViewedParameter"
    """ Entities containing inside this container """

    _entity_reader_class = ViewedParameterReader
    """ Reader that is responsible for downloading viewed parameters from the database """

    _entity_filter_list = {
        'category': (CategoryRecord, None,),
        'user': (User, None,),
    }
    """ List of all available filters that are used within a given category """

    def _subcontainer_condition(self):
        """
        Returns True if entity filters are adjusted enough to activate the swapping function
        i.e., when the entity filters are specified some sub-container within which the entities are allowed to swap
        """
        return self.category is not None and self.user is not None

    def _get_subcontainer_queryset(self):
        """
        Returns the QuerySet object that reveals Django models related to all entities within the container
        """
        return LabjournalParameterView.objects.filter(
            project_id=self.category.project.id,
            category_id=self.category.id,
            user_id=self.user.id,
        )
