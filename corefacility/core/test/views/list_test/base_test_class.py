from math import ceil
import urllib.parse

from rest_framework import status

from core.pagination import CorePagination

from ..base_view_test import BaseViewTest


def profile_provider():
    return [("basic",), ("light",)]


class BaseTestClass(BaseViewTest):
    """
    This is the base test for all views
    """

    _container = None
    """ A copy of the user names """

    _request_path = None
    """ Returns the request path """

    pagination_class = CorePagination
    """ A source for the page size information """

    @staticmethod
    def parse_page_url(url):
        parsed_link = urllib.parse.urlparse(url)
        request_path = parsed_link.path
        query_params = urllib.parse.parse_qs(parsed_link.query)
        query_params = {key: value[0] for key, value in query_params.items()}
        return request_path, query_params

    def _test_search(self, query_params, token_id: str, expected_status_code: int = status.HTTP_200_OK):
        """
        Tries the general field search for the paginated list
        :param query_params: the query parameters that shall be used for searching
        :param token_id: a token ID.
        :param expected_status_code: a status code to expect
        :return: nothing
        """
        headers = self.get_authorization_headers(token_id)
        current_page = 1
        previous_link, next_link = self._test_single_page(self.request_path, query_params, headers, current_page,
                                                          expected_status_code)
        if expected_status_code >= status.HTTP_300_MULTIPLE_CHOICES:
            return
        while next_link is not None:
            current_page += 1
            request_path, query_params = self.parse_page_url(next_link)
            previous_link, next_link = self._test_single_page(request_path, query_params, headers, current_page)
        max_page = current_page
        while previous_link is not None:
            current_page -= 1
            request_path, query_params = self.parse_page_url(previous_link)
            previous_link, next_link = self._test_single_page(request_path, query_params, headers, current_page)
        profile = query_params["profile"]
        page_size = self.pagination_class.PAGE_SIZES[profile]
        desired_page_number = ceil(len(self.container) / page_size)
        if len(self.container) > 0:
            self.assertEquals(max_page, desired_page_number,
                              "The number of pages in the list request is not the same as expected")

    def _test_single_page(self, request_path, query_params, headers, page_number,
                          expected_status_code=status.HTTP_200_OK):
        """
        When the response is paginated, the method provides test for the single list page.
        :param request_path: full path to the request
        :param query_params: query parameters
        :param headers: Request headers
        :param page_number: number of the page to request and test
        :param expected_status_code: status code to be expected
        :return: two-element tuple: URI for the previous page, URI for the next page
        """
        response = self.client.get(request_path, data=query_params, **headers)
        self.assertEquals(response.status_code, expected_status_code, "The entity list response must be successful")
        if response.status_code >= status.HTTP_300_MULTIPLE_CHOICES:
            return None, None
        self.assertEquals(response.data['count'], len(self.container), "Wrong number of items in the response")
        actual_results = response.data["results"]
        profile = query_params["profile"]
        page_size = self.pagination_class.PAGE_SIZES[profile]
        page_offset = (page_number-1) * page_size
        desired_results = self.container[page_offset:page_offset+page_size]
        self._compare_search_result(actual_results, desired_results)
        return response.data['previous'], response.data['next']

    def _test_unpaginated_list(self, query_params, token_id: str, expected_status_code: int = status.HTTP_200_OK):
        """
        Tries general field search for an unpaginated list
        :param query_params: query parameters
        :param token_id: ID for the authorization token
        :param expected_status_code: status code to be expected
        """
        headers = self.get_authorization_headers(token_id)
        response = self.client.get(self.request_path, data=query_params, **headers)
        self.assertEquals(response.status_code, expected_status_code, "The entity list response must be successful")
        if response.status_code >= status.HTTP_300_MULTIPLE_CHOICES:
            return
        actual_results = response.data
        desired_results = self.container[:]
        self.assertEquals(len(actual_results), len(desired_results), "Wrong number of the page size")
        self._compare_search_result(actual_results, desired_results)

    def _compare_search_result(self, actual_results, desired_results):
        """
        Compared the list retrieved by the response with the expected list saved in the object container
        :param actual_results: the list revealed by the response
        :param desired_results: expected list saved in the object container
        """
        self.assertEquals(len(actual_results), len(desired_results), "Wrong number of the page size")
        for result_index in range(len(actual_results)):
            actual_item = actual_results[result_index]
            desired_item = desired_results[result_index]
            self.assert_items_equal(actual_item, desired_item)

    @property
    def container(self):
        if self._container is None:
            raise NotImplementedError("_container public property")
        return self._container

    @property
    def request_path(self):
        if self._request_path is None:
            raise NotImplementedError("_request_path public property")
        return self._request_path

    def assert_items_equal(self, actual_item, desired_item):
        """
        Compares two list item

        :param actual_item: the item received within the response
        :param desired_item: the item taken from the container
        :return: nothing
        """
        raise NotImplementedError("assert_items_equal")


del BaseViewTest
