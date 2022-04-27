from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, \
    ListCreateAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView

from .entity_view_mixin import EntityViewMixin


class EntityListView(EntityViewMixin, ListAPIView):
    """
    Concrete view for listing an entity set.
    """

    def get_serializer_class(self):
        """
        Returns the list serializer class

        :return: the list serializer class
        """
        if self.list_serializer_class is None:
            raise ValueError("Please, define the list_serializer_class property")
        return self.list_serializer_class


class EntityCreateView(EntityViewMixin, CreateAPIView):
    """
    Concrete view for creating entities.
    """
    pass


class EntityRetrieveView(EntityViewMixin, RetrieveAPIView):
    """
    Concrete view for retrieving entities
    """
    pass


class EntityUpdateView(EntityViewMixin, UpdateAPIView):
    """
    Concrete view for updating an entity.
    """
    pass


class EntityListCreateView(EntityViewMixin, ListCreateAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get_serializer_class(self):
        """
        Returns the list serializer class

        :return: the list serializer class
        """
        if self.request.method.lower() == "get":
            return super().get_serializer_class()
        if self.list_serializer_class is None:
            raise ValueError("Please, define the list_serializer_class property")
        return self.list_serializer_class


class EntityRetrieveUpdateView(EntityViewMixin, RetrieveUpdateAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """
    pass


class EntityRetrieveDestroyView(EntityViewMixin, RetrieveDestroyAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    pass


class EntityRetrieveUpdateDestroyView(EntityViewMixin, RetrieveUpdateDestroyAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    pass
