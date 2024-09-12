from django.db import IntegrityError

from ru.ihna.kozhukhov.core_application.entity.field_managers.entity_value_manager import EntityValueManager
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import \
    EntityOperationNotPermitted, EntityDuplicatedException
from ru.ihna.kozhukhov.core_application.models import LabjournalHashtag

from .hashtag_provider import HashtagProvider


class HashtagManager(EntityValueManager):
    """
    This is the base class that allows to add / exclude hashtags from the entity list
    """

    type = None
    """ Types of hashtags this manager adds or removes """

    attachment_model = None
    """ A database where hashtag-to-entity attachments were stored """

    entity_field = None
    """ The entity field inside the joint table """

    hashtag_provider = HashtagProvider()

    @property
    def project(self):
        """
        Returns the related project
        """
        raise NotImplementedError("project")

    def add(self, hashtags):
        """
        Attaches hashtags to a given object

        :param hashtags: list that contains either IDs or description of hashtags. When the list item contains the
            hashtag ID an existent hashtag with a given ID will be added to the hashtag list. When the list item is a
            string this implies that these items refers to non-existent hashtag. New hashtag will be created in this
            case that this newly created hashtag will be added to the hashtag list
        """
        self._check_entity_state()
        self._prepare_field()
        old_hashtag_ids = set(filter(lambda hashtag: isinstance(hashtag, int), hashtags))
        old_hashtag_ids -= {hashtag.id for hashtag in getattr(self._entity, self._field_name)}
        self._check_hashtag_ids(old_hashtag_ids, add_to_field=True)
        new_hashtag_ids = self._create_inexistent_hashtags(
            filter(lambda hashtag: isinstance(hashtag, str), hashtags),
            add_to_field=True,
        )
        final_hashtag_ids = list(old_hashtag_ids) + new_hashtag_ids
        attachment_models = [
            self.attachment_model(**{
                'hashtag_id': hashtag_id,
                self.entity_field: self._entity.id,
            })
            for hashtag_id in final_hashtag_ids
        ]
        self.attachment_model.objects.bulk_create(attachment_models)

    def remove(self, hashtag_ids):
        """
        Detaches hashtags from a given object

        :param hashtag_ids: IDs of detaching hashtags
        """
        self._check_entity_state()
        self._prepare_field()
        existent_hashtag_ids = {hashtag.id for hashtag in self._entity._hashtags}
        input_hashtag_ids = set(hashtag_ids)
        removing_hashtag_ids = existent_hashtag_ids & input_hashtag_ids
        self._entity._hashtags = list(filter(
            lambda hashtag: hashtag.id not in removing_hashtag_ids, self._entity._hashtags
        ))
        self.attachment_model.objects.filter(**{
            'hashtag_id__in': removing_hashtag_ids,
            self.entity_field: self._entity.id,
        }).delete()

    def __iter__(self):
        """
        Iterates over all hashtags within the hashtag list
        """
        hashtag_list = getattr(self._entity, '_' + self._field_name)
        if hashtag_list is not None and len(hashtag_list) > 0:
            for hashtag in hashtag_list:
                yield hashtag

    def __repr__(self):
        self._prepare_field()
        hashtag_representations = [
            '"%s"' % hashtag.description
            for hashtag in getattr(self._entity, '_' + self._field_name)
        ]
        return "[%s]" % ", ".join(hashtag_representations)

    def _prepare_field(self):
        """
        Transforms the hashtag field into the list if it equals to None
        """
        if getattr(self._entity, '_' + self._field_name) is None:
            setattr(self._entity, '_' + self._field_name, list())

    def _check_entity_state(self):
        """
        Ensures that the entity is actually stored in the external storage
        """
        if self._entity.state == 'creating' or self._entity.state == 'deleted':
            raise EntityOperationNotPermitted("Can't add hashtags when the entity is in wrong state")

    def _check_hashtag_ids(self, hashtag_ids, add_to_field=False):
        """
        Tests that all numbers within the given list are valid hashtag IDs

        :param hashtag_ids: IDs to check
        :param add_to_field: add to the hashtag list of the parent entity, in case of success
        """
        if len(hashtag_ids) > 0:
            queryset = LabjournalHashtag.objects \
                .filter(project_id=self.project.id, type=self.type) \
                .filter(pk__in=hashtag_ids)
            hashtag_models = list(queryset)
            if len(hashtag_models) != len(hashtag_ids):
                raise ValueError("The hashtag list contains some numbers that are not valid hashtag IDs")
            if add_to_field:
                getattr(self._entity, '_' + self._field_name).extend([
                    self.hashtag_provider.wrap_entity(hashtag_model)
                    for hashtag_model in hashtag_models
                ])

    def _create_inexistent_hashtags(self, description_list, add_to_field=False):
        """
        Creates bulk of hashtags when their description is given

        :param description_list: a list containing description of newly created hashtags
        :param add_to_field: add to the hashtag list of the parent entity, in case of success
        :return: list of IDs of newly created hashtags
        """
        description_list = list(description_list)
        for _ in \
                filter(lambda description: len(description) < 1 or len(description) > 64, description_list):
            raise ValueError("The string is not suitable for the description value")
        new_hashtag_models = [
            LabjournalHashtag(
                description=description,
                project_id=self.project.id,
                type=self.type,
            )
            for description in description_list
        ]
        for hashtag_model in new_hashtag_models:
            try:
                hashtag_model.save()
            except IntegrityError:
                raise EntityDuplicatedException()
            if add_to_field:
                hashtag_entity = self.hashtag_provider.wrap_entity(hashtag_model)
                getattr(self._entity, '_' + self._field_name).append(hashtag_entity)
        return [hashtag_model.id for hashtag_model in new_hashtag_models]
