from rest_framework import serializers


class EntitySerializer(serializers.Serializer):
    """
    Provides the deserialization facilities for entities
    """

    entity_class = None
    """ Class of the entity that shall be created. """

    def get_entity_class(self):
        """
        Returns an EntityClass or throws ValueError if the entity_class property is empty.

        :return: the Entity class
        """
        if self.entity_class is None:
            raise ValueError("Please, define the entity_class property of your serializer")
        return self.entity_class

    def create(self, data):
        """
        Creates new entity base on the validated data.
        The entity will be automatically stored to the database.

        :param data: The validated data.
        :return: new entity
        """
        entity_class = self.get_entity_class()
        entity = entity_class(**data)
        entity.create()
        return entity

    def update(self, entity, validated_data):
        """
        Updates the entity according to the validated data.

        :param entity: the instance to be updated.
        :param validated_data: valid data to be imposed to the instance
        :return: updated entity
        """
        for key, value in validated_data.items():
            setattr(entity, key, value)
        if entity.state == "changed":
            entity.update()
        return entity
