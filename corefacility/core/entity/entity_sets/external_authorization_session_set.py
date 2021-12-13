from .entity_set import EntitySet


class ExternalAuthorizationSessionSet(EntitySet):
    """
    Provides facilities for looking for some external authorization
    """

    _entity_name = "External authorization session"

    _entity_class = "core.entity.external_authorization_session.ExternalAuthorizationSession"

    _entity_reader_class = None  # TO DO: provide some entity reader

    _entity_filter_list = {}
