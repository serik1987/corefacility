from .model_provider import ModelProvider


class ProjectDataProvider(ModelProvider):
    """
    A special provider that must be used to store all project-related data
    """

    def attach_file(self, entity, name: str, value) -> None:
        """
        Attaches a file to the entity representation located at external entity source. Please note that for
        the project data the uploaded file will not be saved! This is view's responsibility to do this!
        :param entity: the entity to which the file can be attached
        :param name: the field name to which the file should be attached
        :param value: an instance of django.core.files.File object
        :return: nothing
        """
        entity_model = entity._wrapped
        if not isinstance(entity_model, self.entity_model):
            entity_model = self.entity_model.objects.get(pk=entity.id)  # + 1 EXTRA QUERY!
        setattr(entity_model, name, value.name)
        entity_model.save()
        setattr(entity, "_" + name, getattr(entity_model, name))
