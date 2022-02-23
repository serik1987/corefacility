from .entity import Entity
from .entity_sets.project_application_set import ProjectApplicationSet
from .entity_fields.related_entity_field import RelatedEntityField
from .entity_fields.entity_field import EntityField
from .entity_providers.model_providers.project_application_provider import ProjectApplicationProvider


class ProjectApplication(Entity):
    """
    Defines an application attached to a certain project.
    """

    _entity_set_class = ProjectApplicationSet
    """ The entity set class that allows to quickly move towards the EntitySet """

    _entity_provider_list = [ ProjectApplicationProvider() ]
    """ List of entity providers that organize connection between entities and certain data sources """

    _required_fields = ["application", "project", "is_enabled"]
    """
    Defines the list of required entity fields

    The entity can't be created if some required entity fields were not sent
    """

    _public_field_description = {
        "application": RelatedEntityField("core.entity.corefacility_module.CorefacilityModule",
                                          description="The project application"),
        "project": RelatedEntityField("core.entity.project.Project",
                                      description="The project which this application relates to"),
        "is_enabled": EntityField(bool, default=False,
                                  description="Is application enabled")
    }
    """
    A dictionary of EntityField instances that defines how the entity data shall be read or written by the user.

    The EntityField is fully ignored by the entity provider who knows better how to answer this question.
    """
