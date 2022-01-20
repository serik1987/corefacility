from django.core.files import File
from django.db import connection
from django.test.utils import CaptureQueriesContext

from core.entity.entity_exceptions import EntityNotFoundException, EntityOperationNotPermitted
from core.test.media_files_test_case import MediaFilesTestCase


class _AssertLessQueriesContext(CaptureQueriesContext):
    """
    Checks that number of queries doesn't reach such value
    """

    __test_case = None
    __expected_queries = None

    def __init__(self, test_case, num, connection):
        self.__test_case = test_case
        self.__expected_queries = num
        super().__init__(connection)

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return
        executed = len(self)
        self.__test_case.assertLessEqual(
            executed, self.__expected_queries,
            "%d queries executed, %d expected\nCaptured queries were:\n%s" % (
                executed, self.__expected_queries,
                '\n'.join(
                    '%d. %s' % (i, query['sql']) for i, query in enumerate(self.captured_queries, start=1)
                )
            )
        )


class BaseTestClass(MediaFilesTestCase):
    """
    This is the base test class for all entity tests.

    We advise to extend the following methods:
    assertEntityFound - ensure that all entity fields were loaded properly
    """

    POSITIVE_TEST_CASE = 0
    NEGATIVE_TEST_CASE = 1

    TEST_FIND_BY_ID = 0
    TEST_FIND_BY_ALIAS = 1
    TEST_FIND_BY_INDEX = 2
    TEST_SLICING = 3
    TEST_ITERATION = 4
    TEST_COUNT = 5

    _container = None
    """ Defines the container (an instance of EntitySetObject) to test """

    __entity_filters = None

    @property
    def container(self):
        if self._container is None:
            raise NotImplementedError("BaseTestClass._container: the instance value shall be assigned during "
                                      "the setUp")
        else:
            return self._container

    def _test_all_access_features(self, feature_index, arg, test_type):
        """
        Tests all entity reading features

        :param feature_index: entity reading feature to test:
            0 - search by ID
            1 - search by alias
            2 - search by item index in the entity set
            3 - slicing
            4 - iterating
            5 - counting entity number
        :param arg: depends on testing feature:
            for searching by ID: entity index within the entity set object
            for searching by alias: entity alias
            for searching by item index: item index
            for slicing: a tuple containing start and stop indices and slice step
            for iteration: useless
            for entity counting: useless
        :param test_type: 0 for positive test, 1 for negative test, useless for iteration and counting
        :return: nothing
        """
        callback, args = {
            self.TEST_FIND_BY_ID: (self._test_find_by_id, (arg, test_type)),
            self.TEST_FIND_BY_ALIAS: (self._test_find_by_alias, (arg, test_type)),
            self.TEST_FIND_BY_INDEX: (self._test_object_index, (arg, test_type)),
            self.TEST_SLICING: (self._test_object_slice, (arg, test_type)),
            self.TEST_ITERATION: (self._test_object_iteration, ()),
            self.TEST_COUNT: (self._test_entity_count, ())
        }[feature_index]
        if len(args) > 0 and isinstance(args[0], tuple):
            args = (*args[0], args[1])
        callback(*args)

    def _test_find_by_id(self, index, test_type):
        """
        Provides positive of negative test of finding using a certain ID

        :param index: for positive test: index of an existent item within the container. For negative test:
            some useless value
        :param test_type: 0 for positive test case, 1 for negative test case
        :return: nothing
        """
        entity_set = self.get_entity_set()
        if test_type == self.NEGATIVE_TEST_CASE:
            try:
                max_id = max(self._container, key=lambda entity: entity.id).id
            except ValueError:
                max_id = 0
            with self.assertRaises(EntityNotFoundException, msg="The entity with inexistent ID was found"):
                entity_set.get(max_id+1)
            return
        expected_entity = self._container[index]
        actual_entity = entity_set.get(expected_entity.id)
        self.assertEntityFound(actual_entity, expected_entity, "The found entity was not properly loaded")

    def _test_find_by_alias(self, alias, test_type):
        """
        Provides positive or negative finding using a certain alias

        :param alias: alias to check
        :param test_type: 0 for positive test, 1 for negative test
        :return: nothing
        """
        entity_set = self.get_entity_set()
        if test_type == self.NEGATIVE_TEST_CASE:
            with self.assertRaises(EntityNotFoundException,
                                   msg="Entity with non-existent alias '%s' was found" % alias):
                entity_set.get(alias)
            return
        actual_entity = entity_set.get(alias)
        expected_entity = self.container.get_by_alias(alias)
        self.assertEntityFound(actual_entity, expected_entity,
                               "Fail to find entity with alias '%s'" % alias)

    def _test_object_iteration(self):
        """
        Tests object iteration

        :return: nothing
        """
        entity_set = self.get_entity_set()
        index = 0
        for actual_entity in entity_set:
            expected_entity = self.container[index]
            self.assertEntityFound(actual_entity, expected_entity,
                                   "Unexpected objects found during the object iteration")
            index += 1

    def _test_object_index(self, index, test_type):
        """
        Tests object indexing (not slicing)

        :param index: Object index to test
        :param test_type: 0 for positive test 1 for negative test
        :return: nothing
        """
        entity_set = self.get_entity_set()
        if test_type == self.NEGATIVE_TEST_CASE:
            with self.assertRaises(EntityNotFoundException, msg="Entity with unexpected index i=%d was found" % index):
                entity = entity_set[index]
            return
        actual_entity = entity_set[index]
        expected_entity = self.container[index]
        self.assertEntityFound(actual_entity, expected_entity,
                               "Entity indexation test: entity list is mixed or corrupted")

    def _test_object_slice(self, start, stop, step, test_type):
        """
        Tests the entity set slicing operation

        :param start: start index in the slice
        :param stop: stop index in the slice
        :param step: slice step
        :param test_type: 0 for positive test, 1 for negative test
        :return: nothing
        """
        entity_set = self.get_entity_set()
        if test_type == self.NEGATIVE_TEST_CASE:
            with self.assertRaises(EntityOperationNotPermitted,
                                   msg="entity slicing on %s:%s:%s is OK" % (start, stop, step)):
                actual_entity_list = entity_set[start:stop:step]
            return
        actual_entity_list = entity_set[start:stop:step]
        expected_entity_list = self.container[start:stop:step]
        self.assertEquals(len(actual_entity_list), len(expected_entity_list),
                          "entity slicing on %s:%s:%s: number of items retrieved is not the same as expected"
                          % (start, stop, step))
        for i in range(len(actual_entity_list)):
            self.assertEntityFound(actual_entity_list[i], expected_entity_list[i],
                                   "entity slicing on %s:%s:%s: the list returned is incorrect or invalid"
                                   % (start, stop, step))

    def _test_entity_count(self):
        """
        Tests counting overall number of elements

        :return: nothing
        """
        entity_set = self.get_entity_set()
        actual_entity_count = len(entity_set)
        expected_entity_count = len(self._container)
        self.assertEquals(actual_entity_count, expected_entity_count,
                          "Number of entity items is not the same as expected")

    @staticmethod
    def practise_sql_query(query, *args):
        """
        If you want to see SQL data before their interpretation as entities use this method.

        :param query: SQL query. You can use the whole string as well as string fragment.
        :param args: Arguments in case of prepared query
        :return: nothing
        """
        with connection.cursor() as cursor:
            cursor.execute(query, args)
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                print(row)

    @staticmethod
    def load_random_avatars(container, entity_indices, field_name, files):
        """
        Attaches random avatars to the field indices

        :param container: container containing entitites to which you need to attach files
        :param entity_indices: indices of entities to which the avatars shall be attached
        :param field_name: field name to which the avatar should be attached
        :param files: all files in a format received from the data provider
        :return: nothing
        """
        if len(entity_indices) != len(files):
            raise ValueError("There must be as many files as entity indices")
        for i in range(len(files)):
            entity = container[entity_indices[i]]
            filename, _, _ = files[i]
            file_object = File(open(filename, "rb"))
            file_field = getattr(entity, field_name)
            file_field.attach_file(file_object)
            file_object.close()

    def get_entity_set(self):
        """
        Returns the database set corresponding to a certain entity set class

        :return: The entity set for a certain entity set class
        """
        entity_set = self.container.entity_class.get_entity_set_class()()
        if isinstance(self.__entity_filters, dict):
            for name, value in self.__entity_filters.items():
                setattr(entity_set, name, value)
        return entity_set

    def apply_filter(self, name, value):
        """
        Applies some filter

        :param name: filter name
        :param value: filter value
        :return: nothing
        """
        if self.__entity_filters is None:
            self.__entity_filters = dict()
        self.__entity_filters[name] = value
        getattr(self.container, "filter_by_" + name)(value)

    def initialize_filters(self):
        """
        Clears all previously applied filters

        :return: nothing
        """
        self.__entity_filters = dict()

    def assertEntityFound(self, actual_entity, expected_entity, msg):
        """
        Asserts that the entity has been successfully found.
        Class derivatives can re-implement this method to ensure that all entity fields were uploaded successfully.

        :param actual_entity: the entity found in the database
        :param expected_entity: the entity expected to be found in the database
        :param msg: message to print when the entity is failed to be found
        :return: nothing
        """
        self.assertEquals(actual_entity.id, expected_entity.id,
                          "%s. ID of the found entity is not the same as expected" % msg)
        self.assertEquals(actual_entity.state, "loaded",
                          "%s. The found entity state is not 'loaded'" % msg)

    def assertLessQueries(self, num):
        """
        Asserts that the query number is strictly less than expected

        :param num: maximum number of queries asserted
        :return: nothing
        """
        return _AssertLessQueriesContext(self, num, connection)


del MediaFilesTestCase
