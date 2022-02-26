from .entity_value_manager import EntityValueManager


class ProjectApplicationManager(EntityValueManager):
    """
    Defines project applications that are ultimate properties of the Project entity.
    """

    def _get_data(self):
        from core.entity.entity_sets.project_application_set import ProjectApplicationSet
        data = ProjectApplicationSet()
        data.entity_is_enabled = True
        data.project = self._entity
        return data

    def get(self, alias):
        """
        Returns a project that met given conditions

        :param alias: the project alias
        :return: nothing
        """
        data = self._get_data()
        data.application_alias = alias
        return data[0].application

    def __iter__(self):
        """
        Iterates over all project applications

        :return: nothing
        """
        data = self._get_data()
        for app in data:
            yield app.application

    def __len__(self):
        """
        defines total number of elements

        :return: the total number of elements
        """
        return len(self._get_data())
