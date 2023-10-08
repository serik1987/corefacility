from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from ru.ihna.kozhukhov.core_application.entity.entity_sets.failed_authorization_set import FailedAuthorizationSet
from ..models import FailedAuthorizations as FailedAuthorizationModel
from .entity import Entity
from .user import User
from .fields.managed_entity_field import ManagedEntityField
from .field_managers.current_time_manager import CurrentTimeManager
from .fields.ip_address_field import IpAddressField
from .fields.related_entity_field import RelatedEntityField
from .providers.model_providers.failed_authorization_provider import FailedAuthorizationProvider


class FailedAuthorization(Entity):
    """
    Represents one single failed authorization
    """

    _entity_set_class = FailedAuthorizationSet
    """ The entity set class that allows to quickly move towards the EntitySet """

    _entity_provider_list = [FailedAuthorizationProvider()]
    """ List of entity providers that organize connection between entities and certain data sources """

    _required_fields = ['auth_time', 'ip', 'user']
    """
    Defines the list of required entity fields

    The entity can't be created if some required entity fields were not sent
    """

    _public_field_description = {
        'auth_time': ManagedEntityField(CurrentTimeManager, description="Date and time of the failed authorization"),
        'ip': IpAddressField(description="IP address"),
        'user': RelatedEntityField("ru.ihna.kozhukhov.core_application.entity.user.User",
                                   description="User that has been tried to be unsuccessfully authorized")
    }

    @classmethod
    def add(cls, ip_address: str, user: User) -> None:
        """
        Adds new failed authorization
        :param ip_address: IP address from which the authorization has been made
        :param user: the authorized user
        :return: nothing
        """
        authorization = FailedAuthorization()
        authorization.auth_time.mark()
        authorization.ip = ip_address
        authorization.user = user
        authorization.create()

    @classmethod
    def get_failed_authorizations_number(cls, ip: str, user: User, expiry_term: timedelta) -> int:
        auth_set = FailedAuthorizationSet()
        auth_set.expiry_term = expiry_term
        auth_set.ip = ip
        auth_set.user = user
        auth_number = len(auth_set)
        min_time = make_aware(datetime.now() - expiry_term)
        # noinspection PyUnresolvedReferences
        FailedAuthorizationModel.objects.filter(auth_time__lt=min_time).delete()
        return auth_number
