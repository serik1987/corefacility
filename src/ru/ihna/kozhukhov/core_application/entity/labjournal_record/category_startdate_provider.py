from django.db.models import Min, Max

from ru.ihna.kozhukhov.core_application.entity.providers.entity_provider import EntityProvider
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import EntityOperationNotPermitted
from ru.ihna.kozhukhov.core_application.models.labjournal_record import LabjournalRecord, LabjournalRecordType


class CategoryStartdateProvider(EntityProvider):
    """
    Modifies the category start date and finish date when the child record is added, changed and/or modified within
    the category.

    Not suitable for the root record.
    """

    @classmethod
    def update_category_datetime(cls, category):
        """
        Updates the datetime and finish_time fields for particular category and all its ascendants

        :param category: the category object (an instance of models.LabjournalRecord)
        """
        if category is not None:
            children = LabjournalRecord.objects.filter(parent_category=category)
            dates = children.aggregate(min=Min('datetime'), max=Max('datetime'))
            category.datetime = dates['min']
            category.finish_time = dates['max']
            category.save()
            cls.update_category_datetime(category.parent_category)

    def load_entity(self, entity):
        """
        Does nothing because the duplicate control facility was implemented in the previous entity provider

        :param entity: useless
        """
        pass
    
    def create_entity(self, entity):
        """
        Runs automatically when new record is created

        :param entity: the record to be created
        """
        self._update_parent_category(entity)

    def update_entity(self, entity):
        """
        Runs automatically when the record was updated

        :param entity: the record to be updated
        """
        if 'datetime' in entity._edited_fields:
            self._update_parent_category(entity)
        if 'parent_category' in entity._edited_fields:
            raise EntityOperationNotPermitted(
                "The function of modification of the parent category is currently inavailable because it requires "
                "additional computational costs, because it requires additional hours of job and because this is "
                "not required by the application frontend"
            )

    def delete_entity(self, record):
        """
        Deletes the entity from the external entity source

        :param record: the entity to be deleted
        :return: nothing
        """
        parent_category_id = record.parent_category.id
        if parent_category_id is not None:
            parent_category = LabjournalRecord.objects.get(id=parent_category_id)
            self.update_category_datetime(parent_category)

    def _update_parent_category(self, entity):
        """
        Modifies the category start date and finish date according to the newly created entity

        :param entity: the child entity that has been created
        """
        record_row = entity._wrapped
        if record_row is None or not isinstance(record_row, LabjournalRecord) or record_row.id is None:
            raise RuntimeError("Trying to update the parent category when the entity row in the database was not added."
                               " Please, put this provider after the RecordProvider()")
        if record_row.type != LabjournalRecordType.category:
            parent_category = record_row.parent_category
            self.update_category_datetime(parent_category)
            if parent_category is not None:
                entity._relative_time = record_row.datetime - parent_category.datetime
