from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from . import EntityViewMixin


class EntityViewSetMixin(EntityViewMixin):
    """
    Base properties for the entity view sets
    """

    action = None

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (E.g. admins get full serialization, others get basic serialization)
        """
        if self.action is None:
            raise ValueError("The view set action is not defined")
        if self.action == "list":
            serializer_class = self.list_serializer_class
        else:
            serializer_class = self.detail_serializer_class
        if serializer_class is None:
            raise ValueError("Please, set both list_serializer_class and detail_serializer_class properties")
        return serializer_class


class EntityReadOnlyViewSet(EntityViewSetMixin, ReadOnlyModelViewSet):
    """
    Implements all entity reading operations
    """
    pass


class EntityViewSet(EntityViewSetMixin, ModelViewSet):
    """
    Implements all entity CRUD operations
    """
    pass
