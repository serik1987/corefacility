from core.entity.authentication import Authentication

from .entity_set import EntitySet


class ExternalAuthorizationTokenSet(EntitySet):
    """
    Base class for all authorization tokens.
    """

    _entity_filter_list = {
        "authentication": ["core.entity.authentication.Authentication",
                           lambda auth: auth.state != "creating" and auth.state != "deleted"]
    }

    def get(self, lookup):
        """
        Allows to retrieve the external authorization token by ID or authentication

        :param lookup: either ID or authentication object
        :return: the ExternalAuthorizationToken instance
        """
        if isinstance(lookup, Authentication):
            old_auth = None
            if "authentication" in self._entity_filters:
                old_auth = self._entity_filters['authentication']
            self.authentication = lookup
            token = self[0]
            if old_auth is not None:
                self._entity_filters['authentication'] = old_auth
            else:
                del self._entity_filters['authentication']
            return token
        elif isinstance(lookup, str):
            raise ValueError("The alias is not available for external authorization tokens")
        else:
            return super().get(lookup)
