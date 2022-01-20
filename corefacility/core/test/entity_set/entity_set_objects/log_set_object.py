from ipaddress import ip_address

from core.entity.log import Log

from .entity_set_object import EntitySetObject


class LogSetObject(EntitySetObject):
    """
    Defines the list of expected logs that must be found.

    Testing routines will compare such expected logs with actual ones and fail if any discrepancy was found.
    """

    _entity_class = Log

    _user_set_object = None

    def __init__(self, user_set_object, _entity_list=None):
        """
        Initializes the desired log set

        :param user_set_object: the UserSetObject (create this one during the setUpTestData)
        :param _entity_list: (reversed for service purpose only)
        """
        self._user_set_object = user_set_object
        super().__init__(_entity_list)

    def clone(self):
        """
        Returns an exact copy of the entity set. During the copy process the entity list but not entities itself
        will be copied

        :return: the cloned object
        """
        return self.__class__(self._user_set_object, _entity_list=list(self._entities))

    def sort(self):
        """
        Sorts all entities in proper order

        :return: nothing
        """
        self._entities = list(sorted(self._entities, key=lambda log: log.request_date.get(), reverse=True))

    def filter_by_request_date_from(self, value):
        self._entities = list(filter(lambda log: log.request_date.get() >= value, self._entities))

    def filter_by_request_date_to(self, value):
        self._entities = list(filter(lambda log: log.request_date.get() <= value, self._entities))

    def filter_by_ip_address(self, value):
        value = ip_address(value)
        self._entities = list(filter(lambda log: log.ip_address == value, self._entities))

    def filter_by_user(self, user):
        self._entities = list(filter(lambda log: log.user is not None and log.user.id == user.id, self._entities))

    def _new_entity(self, **entity_fields):
        """
        Creates new entity with given initial parameters

        :param entity_fields: the initial parameters passed here from the data provider
        :return: nothing
        """
        entity = super()._new_entity(**entity_fields)
        entity.request_date.mark()
        return entity

    def data_provider(self):
        sample_data = []
        for sample_data_info in """None, None, None, None
/path/to/resource/1/, GET, 127.0.0.1, None
/path/to/resource/2/, POST, ::1, None
/path/to/resource/2/, DELETE, 2001:db8:0:0:1::1, 0
/path/to/resource/1/, DELETE, 8.8.8.8, 1
None, POST, 8.8.8.8, 0
None, GET, 2001:db8:0:0:1::1, 1
/path/to/resource/1/, None, ::1, 0
/path/to/resource/2/, None, 127.0.0.1, 1
/path/to/resource/2/, GET, None, 2
/path/to/resource/1/, POST, None, 3
None, DELETE, 127.0.0.1, 3
None, DELETE, ::1, 2
/path/to/resource/1/, POST, 2001:db8:0:0:1::1, 2
/path/to/resource/2/, GET, 8.8.8.8, 3
/path/to/resource/2/, None, 8.8.8.8, 4
/path/to/resource/1/, None, 2001:db8:0:0:1::1, 3
/path/to/resource/1/, GET, ::1, 4
None, POST, 127.0.0.1, 4
/path/to/resource/1/, DELETE, None, 4
/path/to/resource/1/, DELETE, None, 0
/path/to/resource/1/, DELETE, 127.0.0.1, 0
/path/to/resource/1/, DELETE, ::1, 3
/path/to/resource/1/, DELETE, 2001:db8:0:0:1::1, None
/path/to/resource/1/, POST, 8.8.8.8, None
/path/to/resource/1/, POST, 8.8.8.8, 1
/path/to/resource/1/, GET, 8.8.8.8, 0
/path/to/resource/1/, None, 8.8.8.8, 2
/path/to/resource/1/, DELETE, 2001:db8:0:0:1::1, 4
/path/to/resource/1/, DELETE, ::1, 1
/path/to/resource/1/, DELETE, 127.0.0.1, 2
/path/to/resource/1/, DELETE, None, 1""".split("\n"):
            log_address, request_method, ipaddr, user_index = sample_data_info.split(", ")
            sample_item = {}
            if log_address != 'None':
                sample_item['log_address'] = log_address
            if request_method != 'None':
                sample_item['request_method'] = request_method
            if ipaddr != 'None':
                sample_item['ip_address'] = ipaddr
            if user_index != 'None':
                user = self._user_set_object[int(user_index)]
                sample_item['user'] = user
            sample_data.append(sample_item)

        return sample_data
