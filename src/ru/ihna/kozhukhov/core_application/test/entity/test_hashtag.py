from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import \
    Hashtag, RecordHashtag, HashtagSet, FileHashtag
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import \
    EntityOperationNotPermitted, EntityFieldRequiredException, EntityDuplicatedException, EntityFieldInvalid, \
    EntityNotFoundException
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType

from .labjournal_test_mixin import LabjournalTestMixin
from .base_test_class import BaseTestClass
from .entity_objects.hashtag_object import HashtagObject
from ..data_providers.field_value_providers import \
    string_provider


def type_class_relation_provider():
    return [
        (LabjournalHashtagType.record, RecordHashtag),
        (LabjournalHashtagType.file, FileHashtag),
    ]


class TestHashtag(LabjournalTestMixin, BaseTestClass):
    """
    General test routines for the Hashtag instances
    """

    _entity_object_class = HashtagObject
    """ A special object class that is used for manipulations of the tested class """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()
        HashtagObject._default_create_kwargs['project'] = cls.optical_imaging

    def test_no_base_class(self):
        """
        Tests that Hashtag is an abstract class
        """
        with self.assertRaises(EntityOperationNotPermitted, msg="Can't create hashtag belonging to the default class"):
            Hashtag()

    @parameterized.expand(string_provider(1, 64))
    def test_description_field(self, initial_value, final_value, exception_to_throw, route_number):
        """
        Field test for the 'description' field

        :param initial_value: the first value to assign
        :param final_value: the second value to assign
        :param exception_to_throw: An exception to be expected or None if no exception is expected
        :param route_number: one out of four basic routes
        """
        self._test_field('description', initial_value, final_value, exception_to_throw, route_number,
                         use_defaults=False,
                         project=self.optical_imaging)

    def test_description_field_required(self):
        """
        Tests that the 'description' field is required
        """
        with self.assertRaises(EntityFieldRequiredException, msg="The 'description' field must be required"):
            record = RecordHashtag(project=self.optical_imaging)
            record.create()

    def test_description_unique(self):
        """
        Tests that the 'description' field must be unique
        """
        object1 = HashtagObject()
        object1.create_entity()
        with self.assertRaises(EntityDuplicatedException, msg="The 'description' field must be unique"):
            object2 = HashtagObject()
            object2.create_entity()

    @parameterized.expand([('user',), (None,),])
    def test_project_field_negative(self, value):
        """
        Provides a negative field test for the 'project' field

        :param value: A value that is attempting to assign
        """
        if value == 'user':
            value = self.optical_imaging.governor
        with self.assertRaises(EntityFieldInvalid,
                               msg="Invalid value was successfully assigned to the 'project' field"):
            hashtag = Hashtag(
                description="решётка",
                project=value,
            )
            hashtag.create()

    def test_project_required(self):
        """
        Tests that the 'project' field is required
        """
        with self.assertRaises(EntityFieldRequiredException, msg="The 'project' field must be required"):
            hashtag = RecordHashtag(description="решётка")
            hashtag.create()

    def test_project_separation(self):
        """
        Tests that hashtags with the same description are allowed to be created in different projects
        """
        hashtag1 = RecordHashtag(description="решётка", project=self.optical_imaging)
        hashtag1.create()
        hashtag2 = RecordHashtag(description="решётка", project=self.the_rabbit_project)
        hashtag2.create()
        hashtag_set = HashtagSet()
        hashtag_set.type = LabjournalHashtagType.record
        hashtag_set.project = self.optical_imaging
        hashtag1 = hashtag_set.get(hashtag1.id)
        self.assertEquals(hashtag1.description, "решётка", "The hashtag description was corrupted")
        with self.assertRaises(EntityNotFoundException, msg="The hashtag was found in bad project"):
            hashtag_set.get(hashtag2.id)
        hashtag_set.project = self.the_rabbit_project
        with self.assertRaises(EntityNotFoundException, msg="The hashtag was found in bad project"):
            hashtag_set.get(hashtag1.id)
        hashtag2 = hashtag_set.get(hashtag2.id)
        self.assertEquals(hashtag2.description, "решётка", "The hashtag description was corrupted")

    def test_type_read_only(self):
        """
        Tests that the 'type' field is required
        """
        self._test_read_only_field('type', LabjournalHashtagType.file, ValueError)

    @parameterized.expand(type_class_relation_provider())
    def test_type_class_relation(self, hashtag_type, hashtag_class):
        """
        Tests that the 'type' field always relates to the hashtag class

        :param hashtag_type: expected value of the 'type' field
        :param hashtag_class: Class of the hashtag to create
        """
        hashtag = hashtag_class(
            description="решётка",
            project=self.optical_imaging
        )
        self.assertEquals(hashtag.type, hashtag_type, "Bad hashtag type")
        hashtag.create()
        self.assertEquals(hashtag.type, hashtag_type, "Bad hashtag type")

    @parameterized.expand(type_class_relation_provider())
    def test_type_class_relation_on_load(self, hashtag_type, hashtag_class):
        """
        Tests that the type/class relation saves even after the hashtag reload
        """
        hashtag = hashtag_class(
            description="решётка",
            project=self.optical_imaging,
        )
        hashtag.create()
        hashtag_set = HashtagSet()
        hashtag_set.project = self.optical_imaging
        hashtag_set.type = hashtag_type
        hashtag = hashtag_set.get(hashtag.id)
        self.assertEquals(hashtag.type, hashtag_type, "Bad hashtag type")
        self.assertIsInstance(hashtag, hashtag_class, "Bad hashtag class")

    def test_type_separation(self):
        """
        Tests that the two hashtags can have different types but the same description
        """
        hashtag1 = RecordHashtag(description = "решётка", project=self.optical_imaging)
        hashtag1.create()
        hashtag2 = FileHashtag(description="решётка", project=self.optical_imaging)
        hashtag2.create()
        hashtag_set = HashtagSet()
        hashtag_set.project = self.optical_imaging
        hashtag_set.type = LabjournalHashtagType.record
        hashtag1 = hashtag_set.get(hashtag1.id)
        self.assertEquals(hashtag1.description, "решётка", "Hashtag description was corrupted")
        with self.assertRaises(EntityNotFoundException, msg="Hashtag type mixed"):
            hashtag_set.get(hashtag2.id)
        hashtag_set.type = LabjournalHashtagType.file
        with self.assertRaises(EntityNotFoundException, msg="Hashtag type mixed"):
            hashtag_set.get(hashtag1.id)
        hashtag2 = hashtag_set.get(hashtag2.id)
        self.assertEquals(hashtag2.description, "решётка", "Hashtag description was corrupted")

    def _check_default_fields(self, entity):
        """
        Checks whether the default fields were properly stored.
        The method deals with default data only.

        :param entity: the entity which default fields shall be checked
        :return: nothing
        """
        self.assertEquals(entity.description, "решётка", "Entity description mismatch")
        self.assertEquals(entity.project.id, self.optical_imaging.id, "Entity project mismatch")
        self.assertEquals(entity.type, LabjournalHashtagType.record, "Entity type mismatch")

    def _check_default_change(self, entity):
        """
        Checks whether the fields were properly changed during the call of the entity_object.change_entity_fields()
        method

        :param entity: the entity to check
        """
        self.assertEquals(entity.description, "прямоугольная решётка", "Entity description mismatch")
        self.assertEquals(entity.project.id, self.optical_imaging.id, "Entity project mismatch")
        self.assertEquals(entity.type, LabjournalHashtagType.record, "Entity type mismatch")


del BaseTestClass
