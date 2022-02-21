from .entity_set import EntitySet
from ..entity_readers.external_authorization_session_reader import ExternalAuthorizationSessionReader


class ExternalAuthorizationSessionSet(EntitySet):
    """
    Provides facilities for looking for some external authorization
    """

    _entity_name = "External authorization session"

    _entity_class = "core.entity.external_authorization_session.ExternalAuthorizationSession"

    _entity_reader_class = ExternalAuthorizationSessionReader

    _entity_filter_list = {}
