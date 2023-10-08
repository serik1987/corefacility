from datetime import timedelta
from ru.ihna.kozhukhov.core_application.entity.readers.failed_authorization_set_reader \
    import FailedAuthorizationSetReader

from ..user import User

from .entity_set import EntitySet


ZERO_EXPIRY_TERM = timedelta(0)


class FailedAuthorizationSet(EntitySet):
    """
    Manages the set of different failed authorizations
    """

    _entity_name = "Failed authorization"
    """ A human-readable entity name used for logging """

    _entity_class = 'ru.ihna.kozhukhov.core_application.entity.failed_authorization.FailedAuthorization'
    """ Defines the entity class. Pass string value to this field to prevent circular import """

    _entity_reader_class = FailedAuthorizationSetReader
    """
    Defines the entity reader class. The EntitySet interacts with external data source through the entity
    readers.
    """

    _entity_filter_list = {
        'expiry_term': [timedelta, lambda value: -value if value < timedelta(0) else value],
        'user': [User, None],
        'ip': [str, None]
    }
