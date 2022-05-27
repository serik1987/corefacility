from rest_framework.exceptions import NotFound

from ..entity.entity_sets.entity_set import EntitySet
from ..entity.entity_exceptions import EntityNotFoundException


class EntityViewMixin:
    """
    This is the base mixin for all views that provide CRUD (Create, Read, Update, Delete) operations with
    entities and entity sets.
    """

    entity_set_class = None
    """ The entity set that will be used for entity search """

    paginator_class = None
    """ The entity set that will be used for pagination features """

    list_serializer_class = None
    """ Serializer for entity lists """

    detail_serializer_class = None
    """ Serializer for entity create, read, update, delete """

    lookup_url_kwarg = "lookup"
    """ The parameter in URL route that will be referred to as the lookup field """

    lookup_value_regex = '[a-zA-Z0-9_\\-.]+'
    """ Regular expression for validation of the lookup URL kwarg """

    list_filters = {}
    """ Filters for the entity list """

    @classmethod
    def get_entity_or_404(cls, entity_set, lookup_value):
        """
        Returns the EntitySet instance or throws 404 exception if no such instance exists

        :param entity_set: the entity set where the instance shall be found.
        :param lookup_value: a characterized entity lookup value (ID, string or UUID).
        :return: nothing
        """
        try:
            entity = entity_set.get(lookup_value)
        except (ValueError, EntityNotFoundException):
            raise NotFound()
        return entity

    @classmethod
    def standard_filter_function(cls, filter_param, filter_type):
        """
        Returns a standard filter function.
        Such function gets the filter parameter from the response query parameters and transforms it
        using filter_type transformation function.

        :param filter_param: name of the filter_param in query_params array
        :param filter_type: the filter type or conversion function to the appropriate filter type
        :return: a standard filter function
        """
        def filter_function(query_params):
            if filter_param in query_params:
                value = filter_type(query_params[filter_param])
            else:
                value = None
            return value
        return filter_function

    @classmethod
    def default_filter_function(cls, filter_value):
        """
        Returns the default filter function.
        Such a function always apply certain function to the filter

        :param filter_value: the value to apply
        :return: a filter function
        """
        def filter_function(query_params):
            return filter_value
        return filter_function

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (E.g. admins get full serialization, others get basic serialization)
        """
        if self.detail_serializer_class is None:
            raise ValueError("Please, define the detail_serializer_class property")
        return self.detail_serializer_class

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (E.g. return a list of items that is specific to the user)
        """
        if not isinstance(self.entity_set_class, type) or not issubclass(self.entity_set_class, EntitySet):
            raise ValueError("The property 'entity_set_class' for the %s is undefined or invalid" %
                             self.__class__.__name__)
        return self.entity_set_class()

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        entity_set = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg
        lookup_value = self.kwargs[lookup_url_kwarg]
        try:
            lookup_value = int(lookup_value)
        except ValueError:
            pass
        entity = self.get_entity_or_404(entity_set, lookup_value)
        self.check_object_permissions(self.request, entity)
        return entity

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for filter_name, filter_function in self.list_filters.items():
            filter_value = filter_function(self.request.query_params)
            if filter_value is not None:
                setattr(queryset, filter_name, filter_value)
        return queryset
