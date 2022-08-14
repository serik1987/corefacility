from django.db import transaction
from django.utils.module_loading import import_string

from .entity_exceptions import EntityOperationNotPermitted, EntityProvidersNotDefined, EntityFieldInvalid


class Entity:
    """
    Entity is the most common way to represent an object stored on hard disk or at the database.

    Entity is a decorator for django.db.models.Model that facilitates solving the following goals:

    1. Entities provide unified and simplified interface for accessing the object lists. Entities
    waive a final user from writing and profiling numerous applications of filters and many other
    properties of the Manager instance. As a result, entities always provide optimal number of
    queries and column sets.

    2. Entities optimize the database reading procedure. When you try to find entity stored on the
    database the Entity defines whether this job has been done by raw SQL request or by using the
    Manager object. The most efficient way will be selected.

    3. Entities synchronize the data among different sources. E.g., if the same user account information
    is saved into hard disk drives (in /etc/passwd, /etc/shadow, /etc/group) and the database
    both sources will be updated during performance of the writing operations.

    4. Entities also provide the data validation control by means of additional restrictions that are valid
    either on system or on user level

    NOTE. The entities are not a substitution for REST framework serializers. The goal of the entity is just
    to say the user that something goes wrong. Entity doesn't know where it actually goes wrong.

    NOTE # 2. The entity just guarantees that technical limitations of all external sources and current data
    structure allows you to save the data in proper way. The Entity doesn't know whether any string
    (except alias due to safety reasons) contain proper amount of symbols.

    5. The request atomicity is provided on the Entity level
    """

    _id = None
    """ The entity ID or None if the entity is not stored in the database"""

    _entity_set_class = None
    """ The entity set class that allows to quickly move towards the EntitySet """

    _entity_provider_list = []
    """ List of entity providers that organize connection between entities and certain data sources """

    _wrapped = None
    """
    The field must be read and write by the entity provider: when the provider loads the entity from an external
    source it sets the underlying object (or at least 'I have been loaded this entity' mark) as the value of this
    property. Next, during the entity update such a '_wrapped' property will facilitate the update process
    
    Note that this field is completed by only such entity provider that is called by the entity reader.
    """

    _public_fields = None
    """
    Public entity fields. The public entity fields can be read by the user and can be set by the user. Each
    set to the public entity field changes the model state.
    
    To get/set public fields just access related properties like:
    
    project.alias # ===> 'vasomotor-oscillations'
    project.alias = 'vasomotor-oscillations' # sets the entity field value and changes the model state
    """

    _required_fields = []
    """
    Defines the list of required entity fields
    
    The entity can't be created if some required entity fields were not sent
    """

    _edited_fields = None
    """
    Defines the set of edited fields. Each time you set up the field value number size of this set is increased by
    one and the model state transforms to "changed". However, when the entity transforms to the 'saved' state
    this set is cleared.
    """

    _public_field_description = {}
    """
    A dictionary of EntityField instances that defines how the entity data shall be read or written by the user.
    
    The EntityField is fully ignored by the entity provider who knows better how to answer this question.
    """

    __state = None

    @classmethod
    def get_entity_set_class(cls):
        """
        Defines the class of the EntitySet. The class must be extension of the EntitySet class

        :return: the EntitySet subclass used for managing this particular entity
        """
        if cls._entity_set_class is not None:
            return cls._entity_set_class
        else:
            raise NotImplementedError("Entity: please, redefine the _entity_set_class field or get_entity_class() "
                                      "method")

    @classmethod
    def get_entity_class_name(cls):
        """
        Returns a human-readable entity class name

        :return: a human-readable entity class name
        """
        if cls._entity_set_class is not None:
            return cls._entity_set_class._entity_name
        else:
            return cls.__name__

    @classmethod
    def check_entity_providers_defined(cls):
        """
        Throws an exception if no entity provider is defined
        """
        if cls._entity_provider_list is None or len(cls._entity_provider_list) == 0:
            raise EntityProvidersNotDefined()

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
        self._public_fields = {}
        self._edited_fields = set()
        if "_src" in kwargs:
            self._wrapped = kwargs["_src"]
            for name, value in kwargs.items():
                if name[0] != "_":
                    setattr(self, "_" + name, value)
            self.__state = "loaded"
        else:
            self.__state = "creating"
            for name, value in kwargs.items():
                try:
                    setattr(self, name, value)
                except ValueError:
                    raise ValueError("The field '%s' is not writable" % name)
                except EntityFieldInvalid:
                    raise EntityFieldInvalid(name)

    @property
    def id(self):
        """
        Returns the entity ID
        When you store the entity on the database, a unique ID number is assigned to the entity by
        the database engine.

        :return: The entity ID if the entity has been stored in the database or None otherwise
        """
        return self._id

    @property
    def state(self):
        """
        State of the entity

        :return: one of the following string:
            'creating' the entity is created but no entity source knows about it. One need to save the entity
            'loaded' the entity was loaded from the database, it presents in the entity sources but there is
                no guarantee that all information among sources is properly synchronized
            'changed' the entity has been changed. The entity is presented at all its sources but the information
                contained in the sources is deprecated and must be updated
            'saved' the entity was saved in the sources, the information in the sources is guaranteed to by
                synchronized and up to date
            'deleted' the entity has been deleted from any external source
        """
        return self.__state

    def create(self):
        """
        Creates the entity on the database and all its auxiliary sources

        :return: nothing
        """
        if self.state != "creating":
            raise EntityOperationNotPermitted()
        self.check_entity_providers_defined()
        for field in self._required_fields:
            if field not in self._public_fields:
                raise EntityFieldInvalid(field)
        with self._get_transaction_mechanism():
            for provider in self._entity_provider_list:
                another_entity = provider.load_entity(self)
                if another_entity is None:
                    provider.create_entity(self)
                else:
                    provider.resolve_conflict(self, another_entity)
            self._edited_fields = set()
            self.__state = "saved"

    def update(self):
        """
        Updates the entity to the database and all its auxiliary sources

        The update is not possible when the entity state is not 'changed'

        :return: nothing
        """
        if self.state != "changed":
            raise EntityOperationNotPermitted()
        self.check_entity_providers_defined()
        with self._get_transaction_mechanism():
            for provider in self._entity_provider_list:
                provider.update_entity(self)
        self._edited_fields = set()
        self.__state = "saved"

    def delete(self):
        """
        Deletes the entity from the database and all its auxiliary sources

        The entity can't be deleted when it still 'creating'

        :return: nothing
        """
        if self.state == "creating" or self.state == "deleted":
            raise EntityOperationNotPermitted()
        self.check_entity_providers_defined()
        with self._get_transaction_mechanism():
            for provider in self._entity_provider_list:
                provider.delete_entity(self)
            self._id = None
            self._edited_fields = set()
            self.__state = "deleted"

    def __str__(self):
        """
        Returns a human-readable string representation of an object used for debugging or logging purpose

        :return: the human-readable string representation of an object
        """
        s = repr(self)
        s += "\n==============================================================================\n"
        for name, value in self._public_field_description.items():
            v = getattr(self, name)
            if isinstance(v, Entity):
                v = repr(v)
            s += "%s [%s]: %s\n" % (value.description, name, v)
        return s

    def __repr__(self):
        """
        Returns a short entity representation used for debugging purpose only

        :return: a short entity representation
        """
        s = self.get_entity_class_name()
        if self.id is not None:
            s += " (ID = %s) " % self.id
        else:
            s += " (ID is not assigned) "
        s += self.state.upper()
        return s

    def __getattr__(self, name):
        """
        Gets the public field property.

        If such property doesn't exist AttributeError will be thrown

        :param name: property name
        :return: property value
        """
        EntityValueManager = import_string("core.entity.entity_fields.EntityValueManager")
        if name in self._public_fields:
            description = self._public_field_description[name]
            raw_value = self._public_fields[name]
            value = description.proofread(raw_value)
            if isinstance(value, EntityValueManager):
                value.entity = self
                value.field_name = name
            return value
        elif name[0] == '_' and name[1:] in self._public_fields:
            return self._public_fields[name[1:]]
        elif name in self._public_field_description:
            description = self._public_field_description[name]
            value = description.default
            if isinstance(value, EntityValueManager):
                value.entity = self
                value.field_name = name
            return value
        elif name[0] == '_' and name[1:] in self._public_field_description:
            description = self._public_field_description[name[1:]]
            value = description.default
            if isinstance(value, EntityValueManager):
                value = None
            return value
        else:
            raise AttributeError("'%s' is not a valid public property of the '%s'" % (name, self.__class__.__name__))

    def __setattr__(self, name, value):
        """
        Sets the public field property.

        If the property name is not within the public or private fields the function throws AttributeError

        :param name: public, protected or private field name
        :param value: the field value to set
        :return: nothing
        """
        if name in self._public_field_description:
            description = self._public_field_description[name]
            raw_value = description.correct(value)
            self._public_fields[name] = raw_value
            self._edited_fields.add(name)
            if self.__state == "saved" or self.__state == "loaded":
                self.__state = "changed"
        elif name[0] == '_' and name[1:] in self._public_field_description:
            self._public_fields[name[1:]] = value
        else:
            super().__getattribute__(name)
            super().__setattr__(name, value)

    def notify_field_changed(self, field_name):
        """
        When EntityValueManager changes some of the entity fields it must call this method to notify this entity
        that the field has been change.

        If the EntityValueManager doesn't do this, the entity state will not be considered as 'changed' which
        results to EntityOperationNotPermitted exception.

        :param field_name: the field name that has been changed by the field manager
        :return: nothing
        """
        self._edited_fields.add(field_name)
        if self.__state != "creating":
            self.__state = "changed"

    def _get_transaction_mechanism(self):
        return transaction.atomic()
