from rest_framework.generics import CreateAPIView

from .base_category import BaseCategoryView


class CategoryView(BaseCategoryView, CreateAPIView):
    """
    List of category record (GET) or Add record to a category (POST)
    """

    def list(self, request, *args, **kwargs):
        """
        Lists the record set

        :param request: HTTP request for the item listing
        :param args: positional arguments from the request path parsing
        :param kwargs: keyword arguments from the request path parsing
        """
        response = super().list(request, *args, **kwargs)
        response.data = {
            'records': response.data,
            'descriptors': None,
            'viewed_parameters': None,
        }
        return response
