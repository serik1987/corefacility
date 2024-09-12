from datetime import datetime

from django.test import TestCase
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import DataRecord, RootCategoryRecord, RecordSet
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor import BooleanParameterDescriptor, \
    ParameterDescriptorSet
from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import RecordHashtag, Hashtag, FileHashtag, \
    HashtagSet
from ru.ihna.kozhukhov.core_application.models import \
    LabjournalHashtagRecord, LabjournalDescriptorHashtag, LabjournalFileHashtag
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalRecordType, LabjournalHashtagType
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import \
    EntityOperationNotPermitted, EntityDuplicatedException

from .labjournal_test_mixin import LabjournalTestMixin

entities_to_test = 'record', 'descriptor'

def entities_provider():
    return [(entity,) for entity in entities_to_test]

def hashtags_created_provider():
    data = [
        (['grating'], None,),
        (['grating', 'propofol'], None,),
        (['grating', 'retinotopy', 'trees'], None,),
        (['grating', 'retinotopy'], None,),
        (['propofol', 'arduam', 'dexamethasone'], None,),
        (['grating', 'propofol', 'trees'], None,),
        (['propofol'], None,),
        ([], None,),
        (['propofol', 'arduan'], None,),
        ([''], ValueError,),
        (["="*64], None,),
        (["="*65], ValueError,),
        (['bad_hashtag'], EntityDuplicatedException,),
        ([1234], ValueError,),
    ]
    return [
        (entity_name, hashtags_to_add, exception_to_throw)
        for entity_name in entities_to_test
        for (hashtags_to_add, exception_to_throw) in data
    ]

def hashtags_double_add_provider():
    data = [
        (['grating', 'retinotopy'], ['grating', 'retinotopy', 'trees']),
        (['grating', 'retinotopy'], ['propofol']),
        (['grating', 'retinotopy', 'trees'], []),
        (['grating', 'retinotopy'], []),
        (['grating', 'retinotopy', 'trees'], ['grating']),
        (['grating', 'retinotopy', 'trees'], ['grating', 'propofol', 'trees']),
        (['grating'], []),
        (['grating'], ['propofol', 'arduan']),
        (['grating'], ['grating', 'propofol', 'trees']),
        (['grating', 'retinotopy', 'trees'], ['grating', 'retinotopy']),
        (['grating', 'retinotopy', 'trees'], ['propofol', 'arduan', 'dexamethasone']),
        (['grating', 'retinotopy'], ['trees', 'propofol']),
        (['grating'], ['trees']),
    ]
    return [
        (entity_name, initial_value, final_value, reload_required)
        for entity_name in entities_to_test
        for initial_value, final_value in data
        for reload_required in (True, False)
    ]

def hashtags_remove_provider():
    hashtag_add_list = ([], ['grating'], ['grating', 'retinotopy'], ['grating', 'retinotopy', 'trees'])
    hashtag_remove_list = hashtag_add_list + ([1234], ['propofol'],)
    return [
        (entity_name, initial_hashtags, removing_hashtags, reload_required)
        for entity_name in entities_to_test
        for initial_hashtags in hashtag_add_list
        for removing_hashtags in hashtag_remove_list
        for reload_required in (False, True)
    ]


class TestHashtagManager(LabjournalTestMixin, TestCase):
    """
    Provides test routines for the RecordHashtagManager, DescriptorHashtagManager and FileHashtagManager
    """

    _grating_hashtag = None
    """ The first hashtag to test """

    _retinotopy_hashtag = None
    """ The second hashtag to test """

    _trees_hashtag = None
    """ The third hashtag to test """

    _sample_hashtags = None
    """ All sample hashtags as description => hashtag dictionary """

    _sample_category = None
    """ Represents some sample category where we will create new records """

    _sample_record = None
    """ Represents a sample record with no hashtags """

    _sample_descriptor = None
    """ Represents a sample parameter descriptor """

    association_models = {
        'record': LabjournalHashtagRecord,
        'descriptor': LabjournalDescriptorHashtag,
        'file': LabjournalFileHashtag,
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()

        cls._grating_hashtag = RecordHashtag(description="grating", project=cls.optical_imaging)
        cls._grating_hashtag.create()

        cls._retinotopy_hashtag = RecordHashtag(description="retinotopy", project=cls.optical_imaging)
        cls._retinotopy_hashtag.create()

        cls._trees_hashtag = RecordHashtag(description="trees", project=cls.optical_imaging)
        cls._trees_hashtag.create()

        cls._sample_hashtags = {
            'grating': cls._grating_hashtag,
            'retinotopy': cls._retinotopy_hashtag,
            'trees': cls._trees_hashtag,
        }

        root_category = RootCategoryRecord(project=cls.optical_imaging)
        cls._sample_category = root_category.children[0]
        cls._sample_record = cls._sample_category.children[0]

        cls._sample_descriptor = BooleanParameterDescriptor(
            category=cls._sample_category,
            identifier="sample_descriptor",
            description="Тестовый параметр",
            required=False,
            record_type=[LabjournalRecordType.data,],
        )
        cls._sample_descriptor.create()

    def setUp(self):
        self._grating_hashtag = TestHashtagManager._grating_hashtag
        self._retinotopy_hashtag = TestHashtagManager._retinotopy_hashtag
        self._trees_hashtag = TestHashtagManager._trees_hashtag
        self._sample_category = TestHashtagManager._sample_category
        self._sample_record = TestHashtagManager._sample_record
        self._sample_hashtags = TestHashtagManager._sample_hashtags
        self._sample_descriptor = TestHashtagManager._sample_descriptor

    @parameterized.expand([('add',), ('remove',),])
    def test_record_creating_state(self, method_name):
        """
        Tests the hashtag add for creating record

        :param method_name: the method to test - 'add' or 'remove'
        """
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The hashtag can't be added to record when this is not in external storage"):
            record = DataRecord()
            getattr(record.hashtags, method_name)([self._grating_hashtag.id])
            print(record)

    @parameterized.expand([('add',), ('remove',)])
    def test_descriptor_creating_state(self, method_name):
        """
        Tests the hashtag add for creating descriptor

        :param method_name: name of the method to test
        """
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The hashtag can't be added to descriptor when this is not in external storage"):
            descriptor = BooleanParameterDescriptor()
            getattr(descriptor.hashtags, method_name)([self._grating_hashtag.id])
            print(descriptor)

    @parameterized.expand([('add',), ('remove',)])
    def test_record_deleted_state(self, method_name):
        """
        Tests the hashtag add for deleted record

        :param method_name: 'add' for testing add() method, 'remove' for testing remove method
        """
        sample_record = RecordSet().get(self._sample_record.id)
        sample_record.delete()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The hashtag can't be added to record when this is not in external storage"):
            getattr(sample_record.hashtags, method_name)([self._grating_hashtag.id])

    @parameterized.expand([('add',), ('remove',), ])
    def test_descriptor_deleted_state(self, method_name):
        """
        Tests the hashtag add for deleted state
        """
        descriptor_set = ParameterDescriptorSet()
        descriptor_set.category = self._sample_descriptor.category
        sample_descriptor = descriptor_set.get(self._sample_descriptor.id)
        sample_descriptor.delete()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The hashtag can't be added to descriptor when this is not in external storage"):
            getattr(sample_descriptor.hashtags, method_name)([self._grating_hashtag.id])

    @parameterized.expand(hashtags_created_provider())
    def test_record_hashtags_created(self, entity_name, hashtag_list, exception_to_throw):
        """
        Tests whether hashtags can be created when the record is in created state

        :param entity_name: type of entity to test: 'record', 'descriptor' or 'file'
        :param hashtag_list: list of all hashtags to add
        :param exception_to_throw: an exception to be expected or None if no exception is expected
        """
        hashtag_list = self._process_hashtag_list(hashtag_list)
        final_hashtag_list = self._get_hashtag_list_for_use(hashtag_list)
        sample_entity = self._create_sample_entity(entity_name)
        if exception_to_throw is None:
            sample_entity.hashtags.add(final_hashtag_list)
            self.assertHashtagList(sample_entity, hashtag_list)
            sample_entity = self._reload_sample_entity(sample_entity, entity_name)
            self.assertHashtagList(sample_entity, hashtag_list)
        else:
            with self.assertRaises(exception_to_throw, msg="Successful execution of the negative case"):
                sample_entity.hashtags.add(final_hashtag_list)

    @parameterized.expand(hashtags_double_add_provider())
    def test_record_double_add(self, entity_name, initial_value, final_value, reload_required):
        """
        Tests whether the add() method can be applied twice

        :param entity_name: what entity to test: 'record', 'descriptor' or 'file'
        :param initial_value: the first bulk of hashtags to add
        :param final_value: the second bulk of hashtags to add
        :param reload_required: whether the entity reload is required after the add of the first hashtag bulk
        """
        initial_value = self._process_hashtag_list(initial_value)
        final_value = self._process_hashtag_list(final_value)
        overall_value = set(initial_value) | set(final_value)
        initial_value_for_add = self._get_hashtag_list_for_use(initial_value)
        final_value_for_add = self._get_hashtag_list_for_use(final_value)
        sample_entity = self._create_sample_entity(entity_name)
        sample_entity.hashtags.add(initial_value_for_add)
        if reload_required:
            sample_entity = self._reload_sample_entity(sample_entity, entity_name)
        sample_entity.hashtags.add(final_value_for_add)
        self.assertHashtagList(sample_entity, overall_value)
        sample_entity = self._reload_sample_entity(sample_entity, entity_name)
        self.assertHashtagList(sample_entity, overall_value)

    @parameterized.expand(hashtags_remove_provider())
    def test_record_remove(self, entity_name, initial_hashtags, removing_hashtags, reload_required):
        """
        Tests the remove() method

        :param entity_name: what entity to test: 'record', 'descriptor' or 'file'
        :param initial_hashtags: initial set of the entities
        :param removing_hashtags: final set of the entities
        :param reload_required: whether the entity should be reloaded immediately before the removal
        """
        initial_hashtags = self._process_hashtag_list(initial_hashtags)
        removing_hashtags = self._process_hashtag_list(removing_hashtags)
        hashtags_to_add = self._get_hashtag_list_for_use(initial_hashtags)
        hashtags_to_remove = self._get_hashtag_list_for_use(removing_hashtags)
        expected_hashtags = set(initial_hashtags) - set(removing_hashtags)
        sample_entity = self._create_sample_entity(entity_name)
        sample_entity.hashtags.add(hashtags_to_add)
        if reload_required:
            sample_entity = self._reload_sample_entity(sample_entity, entity_name)
        sample_entity.hashtags.remove(hashtags_to_remove)
        self.assertHashtagList(sample_entity, expected_hashtags)
        sample_entity = self._reload_sample_entity(sample_entity, entity_name)
        self.assertHashtagList(sample_entity, expected_hashtags)

    @parameterized.expand([('record',), ('descriptor',), ])
    def test_hashtags_bad_project(self, entity_name):
        """
        Tests whether hashtags can be added if they belong to the other project than the entity created

        :param entity_name: what entity to test: 'record', 'descriptor' or 'file'
        """
        sample_entity = self._create_sample_entity(entity_name,
            category=RootCategoryRecord(project=self.the_rabbit_project)
        )
        with self.assertRaises(ValueError, msg="Hashtags from different projects have been successfully mixed"):
            sample_entity.hashtags.add([self._trees_hashtag.id])

    @parameterized.expand([('record',), ('descriptor',),])
    def test_record_hashtags_bad_type(self, entity_name):
        """
        Tests whether file hashtags can be successfully added to records or descriptors.

        :param entity_name: type of the entity to test: 'record' or 'descriptor'
        """
        sample_entity = self._create_sample_entity(entity_name)
        sample_hashtag = FileHashtag(
            description="Hello, World!",
            project=self.optical_imaging,
        )
        sample_hashtag.create()
        with self.assertRaises(ValueError, msg="The file hashtag has been successfully added"):
            sample_entity.hashtags.add([sample_hashtag.id])

    def test_hashtag_access_root_category(self):
        """
        Tests whether the 'hashtags' field is still accessible from the root category
        """
        record = RootCategoryRecord(project=self.optical_imaging)
        with self.assertRaises(AttributeError, msg="The hashtags can't be manipulated for root categories"):
            record.hashtags.add([1, 2, 3])

    @parameterized.expand(entities_provider())
    def test_hashtag_associations_autoremove_on_entity_remove(self, entity_name):
        """
        Tests whether hashtag attachments will be automatically removed when the entity is removed

        :param entity_name: what would you like to test: 'record', 'descriptor', 'file'
        """
        sample_entity = self._create_sample_entity(entity_name)
        sample_entity.hashtags.add([self._grating_hashtag.id])
        sample_entity.delete()
        self.assertEquals(self.association_models[entity_name].objects.count(), 0,
                          "The hashtag associations are not automatically removed on entity remove")

    @parameterized.expand(entities_provider())
    def test_hashtag_associations_autoremove_on_hashtag_remove(self, entity_name):
        """
        Tests whether the hashtag attachment will be automatically removed when the hashtag is removed

        :param entity_name: what would you like to test: 'record', 'descriptor' or 'file'
        """
        hashtag_set = HashtagSet()
        hashtag_set.type = LabjournalHashtagType.record
        hashtag_set.project = self.optical_imaging
        sample_hashtag = hashtag_set.get(self._grating_hashtag.id)
        sample_entity = self._create_sample_entity(entity_name)
        sample_entity.hashtags.add([sample_hashtag.id])
        sample_hashtag.delete()
        sample_entity = self._reload_sample_entity(sample_entity, entity_name)
        for _ in sample_entity.hashtags:
            self.fail("The hashtag associations are not automatically removed on hashtag remove")
        self.assertEquals(self.association_models[entity_name].objects.count(), 0,
            "The hashtag associations are not automatically removed on hashtag remove")

    @parameterized.expand(entities_provider())
    def test_hashtag_add_interaction(self, entity_name):
        """
        Tests that the hashtag attachment on one entity doesn't interact with another attachment on the other entity

        :param entity_name: what would you like to test: 'record', 'descriptor' or 'file'
        """
        entity1 = self._create_sample_entity(entity_name)
        entity2 = self._create_sample_entity(entity_name, alias="other")
        entity1.hashtags.add([self._grating_hashtag.id, self._retinotopy_hashtag.id])
        entity2.hashtags.add([self._grating_hashtag.id, self._trees_hashtag.id])
        entity1 = self._reload_sample_entity(entity1, entity_name)
        entity2 = self._reload_sample_entity(entity2, entity_name)
        self.assertHashtagList(entity1, [self._grating_hashtag, self._retinotopy_hashtag])
        self.assertHashtagList(entity2, [self._grating_hashtag, self._trees_hashtag])

    @parameterized.expand(entities_provider())
    def test_hashtag_remove_interaction(self, entity_name):
        """
        Tests whether detaching hashtag in one entity can influence on hashtags on the other entity

        :param entity_name: what would you like to test: 'record', 'descriptor' or 'file'
        """
        entity1 = self._create_sample_entity(entity_name)
        entity2 = self._create_sample_entity(entity_name, alias="other")
        entity1.hashtags.add([self._grating_hashtag.id, self._retinotopy_hashtag.id])
        entity2.hashtags.add([self._grating_hashtag.id, self._trees_hashtag.id])
        entity1 = self._reload_sample_entity(entity1, entity_name)
        entity2 = self._reload_sample_entity(entity2, entity_name)
        entity1.hashtags.remove([self._grating_hashtag.id])
        entity1 = self._reload_sample_entity(entity1, entity_name)
        entity2 = self._reload_sample_entity(entity2, entity_name)
        self.assertHashtagList(entity1, [self._retinotopy_hashtag])
        self.assertHashtagList(entity2, [self._grating_hashtag, self._trees_hashtag])

    def assertHashtagList(self, entity, expected_hashtags):
        """
        Asserts that the hashtags equal to the expected hashtag list

        :param entity: the entity which hashtag list must be checked
        :param expected_hashtags: hashtag list to be expected (hashtag objects or hashtag description)
        """
        actual_hashtags = {hashtag.description for hashtag in entity.hashtags}
        expected_hashtags = {
            hashtag.description if isinstance(hashtag, Hashtag) else hashtag
            for hashtag in expected_hashtags
        }
        self.assertEquals(actual_hashtags, expected_hashtags, "Hashtag list mismatch")

    def _create_sample_entity(self, entity_name, category=None, alias='the_first'):
        """
        Creates some 'sample' entity for testing purpose

        :param entity_name: what kind of entity to create: 'record', 'descriptor' or 'file'
        :param category: defines the parent category for 'record' and 'descriptor' and useless for 'file'
        :param alias: new alias of the entity
        """
        if category is None:
            category = self._sample_category
        if entity_name == 'record':
            sample_entity = DataRecord(
                parent_category=category,
                alias=alias,
                datetime=datetime(2024, 9, 10, 4, 43),
            )
        elif entity_name == 'descriptor':
            sample_entity = BooleanParameterDescriptor(
                category=category,
                identifier=alias,
                description="another_descriptor",
                required=True,
                record_type=[LabjournalRecordType.data, LabjournalRecordType.service,],
            )
        else:
            raise ValueError("The argument value is not correct")
        sample_entity.create()
        return sample_entity

    def _reload_sample_entity(self, sample_entity, entity_name):
        """
        Reloads the sample entity

        :param sample_entity: the sample entity for reloading
        :param entity_name: type of the sample entity for reloading: 'record', 'descriptor' or 'file'
        :return: the sample record after reloading
        """
        if entity_name == 'record':
            sample_entity = self._sample_category.children.get(sample_entity.id)
        elif entity_name == 'descriptor':
            sample_entity = self._sample_category.descriptors.get(sample_entity.id)
        else:
            raise ValueError("The argument value is not correct")
        return sample_entity

    def _process_hashtag_list(self, hashtag_list):
        """
        Replaces all known hashtag descriptions by hashtags

        :param hashtag_list: hashtag list containing descriptions only
        :return: hashtag list containing both hashtag descriptions and hashtag objects
        """
        final_hashtag_list = [
            self._sample_hashtags[hashtag] if hashtag in self._sample_hashtags else hashtag
            for hashtag in hashtag_list
        ]
        final_hashtag_list = ['grating' if x == 'bad_hashtag' else x for x in final_hashtag_list]
        return final_hashtag_list

    def _get_hashtag_list_for_use(self, hashtag_list):
        """
        Prepares the hashtag list for use in the add() and/or remove methods

        :param hashtag_list: the hashtag list before preparation
        :return: the hashtag list after preparation
        """
        return [
            hashtag.id if isinstance(hashtag, Hashtag) else hashtag
            for hashtag in hashtag_list
        ]
