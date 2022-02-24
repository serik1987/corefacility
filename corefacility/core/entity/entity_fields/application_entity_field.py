from .related_entity_field import RelatedEntityField


class ApplicationEntityField(RelatedEntityField):
    """
    This field is used to store applications.

    Applications are corefacility modules that can be attached to a projects and which access rights can be
    adjusted.
    """

    def __init__(self, description=None):
        """
        Initializes the application entity field.

        :param description: the entity field description
        """
        super().__init__("core.entity.corefacility_module.CorefacilityModule", description)

    def correct(self, value):
        """
        Corrects the related entity field when the user assigns its value to an object

        :param value: the field value the user wants to assign
        :return: the field value that will actually be assigned
        """
        module = super().correct(value)
        if module.state in ("uninstalled", "deleted", "deprecated"):
            raise ValueError("Can't attach the application to the project because its state is not valid")
        if not module.is_application:
            raise ValueError("Can't attach the module to the project because the module is not an application")
        return module

