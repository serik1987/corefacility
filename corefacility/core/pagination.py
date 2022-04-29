from rest_framework.pagination import PageNumberPagination

from .api_exceptions import BadOutputProfileException


class CorePagination(PageNumberPagination):
    """
    Special type of the page number pagination where page_size is different for basic and light output profiles.
    """

    PAGE_SIZES = {
        "basic": 20,
        "light": 6,
    }

    def get_page_size(self, request):
        """
        Returns the page size.

        :param request: REST framework request
        :return: page size (an integer number
        """
        output_profile = request.query_params.get("profile", "basic")
        try:
            page_size = self.PAGE_SIZES[output_profile]
        except KeyError:
            raise BadOutputProfileException()
        return page_size
