from django.utils.translation import gettext_lazy as _

from ru.ihna.kozhukhov.core_application.entity.fields import EntityField, RelatedEntityField, ReadOnlyField
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityOperationNotPermitted
from .category_record import CategoryRecord
from .root_record_provider import RootRecordProvider


class RootCategoryRecord(CategoryRecord):
    """
    Represents single category record
    """

    __root_category_state = None
    """ Entity state overrider """

    _entity_provider_list = [
        RootRecordProvider()
    ]
    """ List of all entity providers that work especially with the root record """

    _required_fields = ['project']
    """ There are no required fields inside the root category record """

    _public_field_description = CategoryRecord._public_field_description.copy()
    del _public_field_description['parent_category']
    del _public_field_description['alias']
    del _public_field_description['checked']
    del _public_field_description['hashtags']
    _public_field_description['project'] = RelatedEntityField(
        "ru.ihna.kozhukhov.core_application.entity.project.Project",
        description="Related project"
    )
    del _public_field_description['relative_time']

    @classmethod
    def get_entity_class_name(cls):
        """
        Returns a human-readable entity class name

        :return: a human-readable entity class name
        """
        return _("Root record")

    def __init__(self, **kwargs):
        """
        Initializes the entity. The entity can be initialized in the following ways:

        1) Entity(field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by another entities, request views and serializers.
        all values passed to the entity constructor will be validated

        2) Entity(_src=some_external_object, id=value0, field1=value1, field2=value2, ...)
        This is how the entity shall be initialized by entity providers when they try to wrap the object.
        See EntityProvider.wrap_entity for details

        :param kwargs: the fields you want to assign to entity properties
        """
        super().__init__(**kwargs)
        self._public_fields['path'] = '/'
        if self.state == "creating":
            self.__root_category_state = "found"
            if self._project is None:
                raise ValueError("You must explicitly specify the 'project' property for the root record")
        if self.state == "loaded":
            self.__root_category_state = "loaded"

    @property
    def is_root_record(self):
        """
        Returns True if record is root record
        """
        return True

    @property
    def id(self):
        """
        Always returns None because the root record can't be stored in the database
        """
        return None

    @property
    def state(self):
        """
        Returns the category state
        """
        if self.__root_category_state is None:
            return super().state
        else:
            return self.__root_category_state

    def create(self):
        """
        Throws an exception because the only root record that is able to exist has already been automatically created
        """
        raise EntityOperationNotPermitted(msg="Can't create one more root record")

    def update(self):
        """
        Stores all changes made to the database
        """
        super().update()
        self.__root_category_state = "saved"

    def delete(self):
        """
        throws an exception because the root record can't be deleted
        """
        raise EntityOperationNotPermitted(msg="The root record can't be deleted")

    def __getattr__(self, name):
        """
        Gets the public field property.

        If such property doesn't exist AttributeError will be thrown

        :param name: property name
        :return: property value
        """
        if name.startswith("custom_"):
            raise AttributeError("Due to technical limitations the custom parameters can't be set for root records")
        return super().__getattr__(name)

    def __setattr__(self, name, value):
        """
        Sets the public field property.

        If the property name is not within the public or private fields the function throws AttributeError

        :param name: public, protected or private field name
        :param value: the field value to set
        :return: nothing
        """
        if name.startswith("custom_"):
            raise AttributeError("Due to technical limitations the custom parameters can't be set for root records")
        previous_state = self.__root_category_state
        super().__setattr__(name, value)
        if name == 'project':
            if len(self._edited_fields) > 1:
                raise RuntimeError("This operation switches from one root record to another one, not modifies "
                                   "an existent root record")
            self._edited_fields.remove(name)
            self.__root_category_state = previous_state
        elif name in self._public_field_description and name != 'user':
            if self.__root_category_state is None or self.__root_category_state == 'found':
                raise RuntimeError("The root category record is read-only when this is in FOUND state")
            else:
                self.__root_category_state = 'changed'
