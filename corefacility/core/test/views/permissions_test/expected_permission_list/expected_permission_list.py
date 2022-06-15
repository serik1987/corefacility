from typing import overload, Iterable, List, Union

from rest_framework import status
from rest_framework.response import Response

from core.entity.group import Group

from .expected_permission import ExpectedPermission
from .exceptions import DataProviderError


class ExpectedPermissionList:
    """
    This is a container that will be used to save list of expected permissions.
    Such expected permissions will be compared to the actual ones at the end of the test case
    """

    _container = None
    _root_group = None

    def __init__(self, source: Union[Response, Iterable[ExpectedPermission]], root_group: Group):
        """
        Initializes the expected permission list

        :param source: the permission list response that shall be transformed to the permission list
        :param root_group: the implied root group
        """
        if isinstance(source, Response):
            self._container = []
            self._get_from_response(source)
        else:
            self._container = list(source)
        self._root_group = root_group

    @property
    def container(self) -> List[ExpectedPermission]:
        """
        An ordered list containing all viewed permissions
        """
        return self._container

    @property
    def root_group(self) -> Group:
        """
        The root group itself
        """
        return self._root_group

    def _get_from_response(self, response: Response) -> None:
        if response.status_code != status.HTTP_200_OK:
            raise DataProviderError()
        self._container = []
        for permission_info in response.data:
            permission = ExpectedPermission(group_id=permission_info['group_id'],
                                            group_name=permission_info['group_name'],
                                            level_alias=permission_info['access_level_alias'])
            self._container.append(permission)

    def __iter__(self):
        """
        Iterates over the permission set

        :return: generator
        """
        for expected_permission in self.container:
            yield expected_permission

    def append(self, item: ExpectedPermission) -> "ExpectedPermissionList":
        """

        :param item: an item to append
        :return: self
        """
        self.container.append(item)
        return self

    def get_by_group_id(self, group_id: int) -> Union[ExpectedPermission, None]:
        """
        Finds permission with a given group ID

        :param group_id: group ID which permission shall be checked
        :return: an instance of ExpectedPermission in case of success, None in case of fail
        """
        permission = None
        for current_permission in self.container:
            if current_permission.group_id == group_id:
                permission = current_permission
        return permission
