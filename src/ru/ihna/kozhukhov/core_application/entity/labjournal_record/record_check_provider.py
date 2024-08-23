from ru.ihna.kozhukhov.core_application.entity.providers.entity_provider import EntityProvider
from ru.ihna.kozhukhov.core_application.models import LabjournalCheckedRecord


class RecordCheckProvider(EntityProvider):
    """
    The provider is responsible for store the information about whether the user checked the record or not.

    Not suitable for the root record.
    """

    def load_entity(self, record):
        """
        Does nothing because this provides doesn't have information about the labjournal records.
        Also, the job for seeking for the record duplicated is accomplished by the previous providers

        :param record: useless
        """
        return None

    def create_entity(self, entity):
        """
        Creates the entity check status if the user context was set

        :param entity: the entity which status must be updated
        """
        if entity.id is None:
            raise RuntimeError("The RecordCheckProvider can't be applied before the RecordProvider")
        if entity._user is not None and entity._checked:
            LabjournalCheckedRecord(record_id=entity.id, user_id=entity._user.id).save()

    def update_entity(self, entity):
        """
        Modifies the entity check status if the user context was set

        :param entity: the entity which status must be modified
        """
        if entity._user is not None and 'checked' in entity._edited_fields:
            desired_check_status = entity._checked
            try:
                actual_status_record = LabjournalCheckedRecord.objects.get(record_id=entity.id, user_id=entity._user.id)
                actual_check_status = True
            except LabjournalCheckedRecord.DoesNotExist:
                actual_status_record = None
                actual_check_status = False
            if desired_check_status and not actual_check_status:
                LabjournalCheckedRecord(record_id=entity.id, user_id=entity._user.id).save()
            if not desired_check_status and actual_check_status:
                actual_status_record.delete()

    def delete_entity(self, entity):
        """
        Does nothing because all necessary rows will be automatically deleted during the execution of the
        foreign key constraints

        :param entity: the entity to be deleted
        """
        pass
