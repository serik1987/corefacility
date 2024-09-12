from datetime import datetime
from django.test import TestCase
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_hashtags import RecordHashtag, FileHashtag, HashtagSet
from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RootCategoryRecord, RecordSet, DataRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_parameter_descriptor import \
    BooleanParameterDescriptor, ParameterDescriptorSet
from ru.ihna.kozhukhov.core_application.exceptions.entity_exceptions import \
    EntityOperationNotPermitted, EntityNotFoundException
from ru.ihna.kozhukhov.core_application.models.enums import LabjournalHashtagType, LabjournalRecordType

from .labjournal_test_mixin import LabjournalTestMixin


def entity_provider():
    return [('record',), ('descriptor',), ]

def entity_manager_provider():
    return [
        (entity_name, method_name)
        for (entity_name,) in entity_provider()
        for method_name in ('add', 'remove')
    ]


def multiple_records_provider():
    primary_duplicated_record_matrix = [
        (0, 0),
        (1, 0), (1, 1),
        (2, 0), (2, 1), (2, 2),
        (3, 0), (3, 1), (3, 2), (3, 3),
        (4, 0), (4, 1), (4, 2), (4, 3), (4, 4),
    ]
    return [
        (entity_name, record_number, duplicated_record_number, hashtag_reload_needed)
        for (entity_name,) in entity_provider()
        for (record_number, duplicated_record_number) in primary_duplicated_record_matrix
        for hashtag_reload_needed in (False, True)
    ]


hashtag_classes = {
    'record': RecordHashtag,
    'file': FileHashtag
}


class TestHashtagEntityManager(LabjournalTestMixin, TestCase):
    """
    Tests the HashtagEntityManager
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()

        cls.chess_hashtag = RecordHashtag(description="шахматный", project=cls.optical_imaging)
        cls.chess_hashtag.create()

        cls.seldom_hashtag = RecordHashtag(description="редкий", project=cls.optical_imaging)
        cls.seldom_hashtag.create()

        cls.most_seldom_hashtag = RecordHashtag(description="редчайший", project=cls.optical_imaging)
        cls.most_seldom_hashtag.create()

        cls.hashtag_collection = {
            'chess': cls.chess_hashtag,
            'seldom': cls.seldom_hashtag,
            'most_seldom': cls.most_seldom_hashtag,
        }

        root_record = RootCategoryRecord(project=cls.optical_imaging)
        cls.sample_category = root_record.children[0]

        category_children = cls.sample_category.children
        cls.all_records = category_children[0:12]
        cls.chess_records = cls.all_records[::2]
        cls.seldom_records = cls.all_records[::3]
        cls.most_seldom_records = cls.all_records[::4]
        cls.record_set_collection = {
            'chess': cls.chess_records,
            'seldom': cls.seldom_records,
            'most_seldom': cls.most_seldom_records,
        }
        cls.record_id_collection = {
            'chess': {record.id for record in cls.chess_records},
            'seldom': {record.id for record in cls.seldom_records},
            'most_seldom': {record.id for record in cls.most_seldom_records},
        }

        cls.all_descriptors = list()
        cls.chess_descriptors = list()
        cls.seldom_descriptors = list()
        cls.most_seldom_descriptors = list()
        for descriptor_index in range(12):
            descriptor = BooleanParameterDescriptor(
                category=cls.sample_category,
                identifier="descriptor%d" % descriptor_index,
                description="Sample identifier",
                required=True,
                record_type=[LabjournalRecordType.data],
            )
            descriptor.create()
            cls.all_descriptors.append(descriptor)
            if descriptor_index % 2 == 0:
                cls.chess_descriptors.append(descriptor)
            if descriptor_index % 3 == 0:
                cls.seldom_descriptors.append(descriptor)
            if descriptor_index % 4 == 0:
                cls.most_seldom_descriptors.append(descriptor)

        cls.descriptor_set_collection = {
            'chess': cls.chess_descriptors,
            'seldom': cls.seldom_descriptors,
            'most_seldom': cls.most_seldom_descriptors,
        }

        cls.descriptor_id_collection = {
            'chess': {descriptor.id for descriptor in cls.chess_descriptors},
            'seldom': {descriptor.id for descriptor in cls.seldom_descriptors},
            'most_seldom': {descriptor.id for descriptor in cls.most_seldom_descriptors}
        }

        cls.entity_set_collection = {
            'record': cls.record_set_collection,
            'descriptor': cls.descriptor_set_collection,
        }

        cls.entity_id_collection = {
            'record': cls.record_id_collection,
            'descriptor': cls.descriptor_id_collection,
        }

        cls.all_entities = {
            'record': cls.all_records,
            'descriptor': cls.all_descriptors,
        }

        cls.chess_hashtag.records.add(cls.chess_records)
        cls.seldom_hashtag.records.add(cls.seldom_records)
        cls.most_seldom_hashtag.records.add(cls.most_seldom_records)

        cls.chess_hashtag.descriptors.add(cls.chess_descriptors)
        cls.seldom_hashtag.descriptors.add(cls.seldom_descriptors)
        cls.most_seldom_hashtag.descriptors.add(cls.most_seldom_descriptors)

    def setUp(self):
        self.chess_hashtag = TestHashtagEntityManager.chess_hashtag
        self.seldom_hashtag = TestHashtagEntityManager.seldom_hashtag
        self.most_seldom_hashtag = TestHashtagEntityManager.most_seldom_hashtag
        self.sample_category = TestHashtagEntityManager.sample_category
        self.hashtag_collection = TestHashtagEntityManager.hashtag_collection
        self.all_records = TestHashtagEntityManager.all_records
        self.chess_records = TestHashtagEntityManager.chess_records
        self.seldom_records = TestHashtagEntityManager.seldom_records
        self.most_seldom_records = TestHashtagEntityManager.most_seldom_records
        self.record_set_collection = TestHashtagEntityManager.record_set_collection
        self.all_descriptors = TestHashtagEntityManager.all_descriptors
        self.chess_descriptors = TestHashtagEntityManager.chess_descriptors
        self.seldom_descriptors = TestHashtagEntityManager.seldom_descriptors
        self.most_seldom_descriptors = TestHashtagEntityManager.most_seldom_descriptors
        self.descriptor_set_collection = TestHashtagEntityManager.descriptor_set_collection
        self.descriptor_id_collection = TestHashtagEntityManager.descriptor_id_collection
        self.entity_set_collection = TestHashtagEntityManager.entity_set_collection
        self.entity_id_collection = TestHashtagEntityManager.entity_id_collection
        self.all_entities = TestHashtagEntityManager.all_entities

    @parameterized.expand(entity_manager_provider())
    def test_hashtag_creating_attachment_to_record(self, entity_name, method_name):
        """
        Tests the hashtag can't be added to entities when the 'hashtag' is in creating state

        :param entity_name: name of the entity to test - 'record', 'descriptor' or 'file'
        :param method_name: what method to test - 'add' or 'remove'
        """
        custom_hashtag = RecordHashtag(
            description="произвольный",
            project=self.optical_imaging,
        )
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The hashtag can't be attached when this is in CREATING state"):
            hashtag_entity_manager = getattr(custom_hashtag, entity_name + 's')
            getattr(hashtag_entity_manager, method_name)(self.entity_set_collection[entity_name]['chess'])

    @parameterized.expand(entity_manager_provider())
    def test_hashtag_deleted_attachment_to_record(self, entity_name, method_name):
        """
        Tests that the hashtag can't be added to entities when the hashtag is in 'deleted' state

        :param entity_name: name of the entity to test: 'record', 'descriptor' or 'file'
        :param method_name: what method to test - 'add' or 'remove'
        """
        hashtag_list = HashtagSet()
        hashtag_list.project = self.optical_imaging
        hashtag_list.type = LabjournalHashtagType.record
        sample_hashtag = hashtag_list.get(self.chess_hashtag.id)
        sample_hashtag.delete()
        with self.assertRaises(EntityOperationNotPermitted,
                               msg="The hashtag can't be attached when this is in DELETED state"):
            hashtag_entity_manager = getattr(sample_hashtag, entity_name + 's')
            getattr(hashtag_entity_manager, method_name)(self.entity_set_collection[entity_name]['chess'])

    @parameterized.expand(multiple_records_provider())
    def test_add_multiple_entities(self, entity_name, entity_number, duplicated_entity_number, hashtag_reload_needed):
        """
        Tests the addition of multiple records

        :param entity_name: What entity to test: 'record', 'descriptor' or 'file'
        :param entity_number: Number of records this hashtag should be added
        :param duplicated_entity_number: Number of records that will be added twice
        :param hashtag_reload_needed: True to test hashtag in LOADED state, False to test hashtag in SAVED state
        """
        entities_to_add = list(self.entity_set_collection[entity_name]['chess'])[:entity_number]
        entity_ids_to_add = {entity.id for entity in entities_to_add}
        sample_hashtag = self.create_sample_hashtag('record')
        if hashtag_reload_needed:
            sample_hashtag = self.reload_sample_hashtag(sample_hashtag)
        getattr(sample_hashtag, entity_name + 's').add(entities_to_add[:duplicated_entity_number])
        getattr(sample_hashtag, entity_name + 's').add(entities_to_add)
        for entity in self.all_entities[entity_name]:
            reloaded_entity = self.reload_sample_entity(entity, entity_name)
            actual_hashtag_ids = {hashtag.id for hashtag in reloaded_entity.hashtags}
            expected_hashtag_ids = self.get_default_entity_hashtags(entity, entity_name)
            if reloaded_entity.id in entity_ids_to_add:
                expected_hashtag_ids.add(sample_hashtag.id)
            self.assertEquals(actual_hashtag_ids, expected_hashtag_ids,
                              "Multiple hashtag add failed: records mismatch!")

    @parameterized.expand(multiple_records_provider())
    def test_remove_multiple_entities(self, entity_name, entity_number, duplicated_entity_number, hashtag_reload_needed):
        """
        Tests the removal of multiple records

        :param entity_name: What entity to test: 'record', 'descriptor' or 'file'
        :param entity_number: Number of records this hashtag should be added
        :param duplicated_entity_number: Number of records that will be added twice
        :param hashtag_reload_needed: True to test hashtag in LOADED state, False to test hashtag in SAVED state
        """
        entities_to_remove = list(self.entity_set_collection[entity_name]['chess'])[:entity_number]
        entity_ids_to_remove = {entity.id for entity in entities_to_remove}
        sample_hashtag = self.create_sample_hashtag('record')
        if hashtag_reload_needed:
            sample_hashtag = self.reload_sample_hashtag(sample_hashtag)
        getattr(sample_hashtag, entity_name + 's').remove(entities_to_remove[:duplicated_entity_number])
        getattr(sample_hashtag, entity_name + 's').remove(entities_to_remove)
        for entity in self.all_entities[entity_name]:
            reloaded_entity = self.reload_sample_entity(entity, entity_name)
            actual_hashtag_ids = {hashtag.id for hashtag in reloaded_entity.hashtags}
            expected_hashtag_ids = self.get_default_entity_hashtags(entity, entity_name)
            if reloaded_entity.id in entity_ids_to_remove and sample_hashtag.id in expected_hashtag_ids:
                expected_hashtag_ids.remove(sample_hashtag.id)
            self.assertEquals(actual_hashtag_ids, expected_hashtag_ids,
                              "Multiple hashtag remove failed: records mismatch!")

    @parameterized.expand(entity_provider())
    def test_add_bad_record_id(self, entity_name):
        """
        Tests the addition of record with bad ID

        :param entity_name: what entity to test: 'record', 'descriptor' or 'file'
        """
        sample_entity = self.create_sample_entity(entity_name)
        bad_id = sample_entity.id
        sample_entity.delete()
        with self.assertRaises(EntityNotFoundException,
                               msg="Hashtag has been successfully added to non-existent entity"):
            getattr(self.chess_hashtag, entity_name + 's').add([bad_id])

    @parameterized.expand(entity_provider())
    def test_add_bad_record_id(self, entity_name):
        """
        Tests whether the remove() works correctly if ID of non-existent entity was put

        :param entity_name: what entity to test: 'record' descriptor' or 'file'
        """
        sample_entity = self.create_sample_entity(entity_name)
        bad_id = sample_entity.id
        sample_entity.delete()
        # Both outcomes are OK: successful execution with no changes and throwing the EntityNotFoundException
        try:
            getattr(self.chess_hashtag, entity_name + 's').remove([bad_id])
        except EntityNotFoundException:
            pass

    @parameterized.expand(entity_provider())
    def test_add_hashtag_to_bad_project(self, entity_name):
        """
        Tests what's happened if we try to add hashtag to some bad project

        :param entity_name: what entity to test: 'record', 'descriptor' or 'file'
        """
        sample_entity = self.create_sample_entity(entity_name, project=self.the_rabbit_project)
        with self.assertRaises(EntityNotFoundException,
                               msg="Hashtag has been successfully added to entity from another project"):
            getattr(self.chess_hashtag, entity_name + 's').add([sample_entity.id])

    @parameterized.expand(entity_manager_provider())
    def test_entity_in_creating_state(self, entity_name, method_name):
        """
        Tests whether the hashtag can be added/removed to/from the entity that is in CREATING state

        :param entity_name: what entity to test: 'record', 'descriptor' or 'file'
        """
        sample_entity = self.create_sample_entity(entity_name, create_in_db=False)
        with self.assertRaises(EntityNotFoundException,
                               msg="Hashtag has been successfully added to the entity in CREATING state"):
            entity_manager = getattr(self.chess_hashtag, entity_name + 's')
            getattr(entity_manager, method_name)([sample_entity])

    @parameterized.expand(entity_manager_provider())
    def test_add_entity_to_file_hashtag_negative(self, entity_name, method_name):
        """
        Tests whether the file hashtag can be added to the record

        :param entity_name: what would you like to test: 'record', 'descriptor' or 'file'
        :param method_name: what method to use: 'add' or 'remove'
        """
        sample_hashtag = self.create_sample_hashtag('file')
        sample_entity = self.create_sample_entity(entity_name)
        with self.assertRaises(AttributeError, msg="The file hashtag can't be added to the record in principle"):
            entity_manager = getattr(sample_hashtag, entity_name + 's')
            getattr(entity_manager, method_name).add([sample_entity])

    def create_sample_hashtag(self, hashtag_type):
        """
        Creates a sample hashtag for the testing purpose

        :param hashtag_type: 'record' for Record hashtag, 'file' for the file hashtag
        :return: the Hashtag instance
        """
        hashtag_class = hashtag_classes[hashtag_type]
        sample_hashtag = hashtag_class(description="grating", project=self.optical_imaging)
        sample_hashtag.create()
        return sample_hashtag

    def create_sample_entity(self, entity_name, project=None, create_in_db=True):
        """
        Creates sample entity for some negative tests

        :param entity_name: what entity to create: 'record', 'descriptor' or 'file'
        :param project: A project the entity must belong to. Default is self.optical_imaging
        :param create_in_db: Store entity to the database
        """
        if project is None:
            category = self.sample_category
        else:
            category = RootCategoryRecord(project=project).children[0]
        if entity_name == 'record':
            sample_entity = DataRecord(
                parent_category=category,
                alias="xxx",
                datetime=datetime(2024, 9, 12, 5, 58)
            )
        elif entity_name == 'descriptor':
            sample_entity = BooleanParameterDescriptor(
                category=category,
                identifier="xxx",
                description="xxx",
                required=False,
                record_type=[LabjournalRecordType.service],
            )
        else:
            raise ValueError("The entity '%s' is not supported" % entity_name)
        if create_in_db:
            sample_entity.create()
        return sample_entity

    def reload_sample_entity(self, entity, entity_name):
        """
        Reloads the entity

        :param entity: entity to reload
        :param entity_name: What would you like to reload: 'record', 'descriptor' or 'file'
        """
        if entity_name == 'record':
            record_set = RecordSet()
            reloaded_entity = record_set.get(entity.id)
        elif entity_name == 'descriptor':
            descriptor_set = ParameterDescriptorSet()
            descriptor_set.category = self.sample_category
            reloaded_entity = descriptor_set.get(entity.id)
        else:
            raise ValueError("reload_sample_entity doesn't work for a given entity_name")
        return reloaded_entity

    def reload_sample_hashtag(self, hashtag):
        """
        Reloads the sample hashtag

        :param hashtag: the hashtag that is required to be reloaded
        :return: hashtag after reloading
        """
        hashtag_set = HashtagSet()
        hashtag_set.project = self.optical_imaging
        hashtag_set.type = LabjournalHashtagType.record
        reloaded_hashtag = hashtag_set.get(hashtag.id)
        return reloaded_hashtag

    def get_default_entity_hashtags(self, entity, entity_name):
        """
        Returns so called 'default' hashtags that contained inside the entity before running the test case

        :param entity: the entity which hashtags must be computed
        :return: the set with expected hashtags
        """
        expected_hashtag_ids = set()
        for standard_hashtag_cue, standard_hashtag_entities in self.entity_id_collection[entity_name].items():
            if entity.id in standard_hashtag_entities:
                expected_hashtag_ids.add(self.hashtag_collection[standard_hashtag_cue].id)
        return expected_hashtag_ids
