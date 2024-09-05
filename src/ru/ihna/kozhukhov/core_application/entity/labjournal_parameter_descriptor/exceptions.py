from django.utils.translation import gettext as _

from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityException


class DuplicatedValueException(EntityException):

    def __init__(self):
        super().__init__(_("The descriptor value with similar ID was created"))
