from collections import defaultdict, namedtuple
from datetime import timedelta
from time import time

from dateutil.parser import parse

from django.db.models import Max
from django.utils.dateparse import parse_duration
from django.utils.duration import duration_string
from django.utils.timezone import make_naive
from parameterized import parameterized

from ru.ihna.kozhukhov.core_application.entity.labjournal_record import RecordSet, RootCategoryRecord, ServiceRecord, \
    CategoryRecord
from ru.ihna.kozhukhov.core_application.entity.labjournal_record.complex_interval import ComplexInterval
from ru.ihna.kozhukhov.core_application.entry_points.authorizations import AuthorizationModule
from ru.ihna.kozhukhov.core_application.models import LabjournalHashtag
from ru.ihna.kozhukhov.core_application.utils import LabjournalCache

from ...data_providers.labjournal_record_search_provider import *
from ...entity_set.entity_set_objects.group_set_object import GroupSetObject
from ...entity_set.entity_set_objects.parameter_descriptor_set_object import ParameterDescriptorSetObject
from ...entity_set.entity_set_objects.project_set_object import ProjectSetObject
from ...entity_set.entity_set_objects.record_hashtag_set_object import RecordHashtagSetObject
from ...entity_set.entity_set_objects.record_set_object import RecordSetObject
from ...entity_set.entity_set_objects.user_set_object import UserSetObject
from .base_test_class import BaseTestClass


class TestCategory(BaseTestClass):
    """
    Tests the category view
    """

    BadHashtag = namedtuple("BadHashtag", ['id', 'description'])

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_base_environment()
        cls.authorize_all_users()
        cls._set_user_checkboxes()

    @classmethod
    def create_base_environment(cls):
        """
        Creates the test environment
        """
        cls.user_set_object = UserSetObject()
        cls.group_set_object = GroupSetObject(cls.user_set_object)
        cls.project_set_object = ProjectSetObject(cls.group_set_object)
        cls.record_set_object = RecordSetObject(cls.user_set_object, cls.project_set_object)
        cls.record_hashtag_set_object = RecordHashtagSetObject(cls.record_set_object)
        cls.parameter_descriptor_set_object = ParameterDescriptorSetObject(cls.record_set_object)
        cls.parameter_descriptor_set_object.set_custom_parameters()
        cls.fill_discrete_parameter_values()
        LabjournalCache().clean_category(RootCategoryRecord(project=cls.record_set_object.the_rabbit_project))

    @classmethod
    def authorize_all_users(cls):
        """
        Authorizes all users that participate in testing
        """
        cls.working_project = cls.record_set_object.the_rabbit_project

        cls.full_user = cls.user_set_object.get_by_alias('user1')
        cls.full_token = AuthorizationModule.issue_token(cls.full_user)

        cls.data_full_user = cls.user_set_object.get_by_alias('user2')
        cls.data_full_token = AuthorizationModule.issue_token(cls.data_full_user)

        cls.data_view_user = cls.user_set_object.get_by_alias('user7')
        cls.data_view_token = AuthorizationModule.issue_token(cls.data_view_user)

        cls.no_access_user = cls.user_set_object.get_by_alias('user10')
        cls.no_access_token = AuthorizationModule.issue_token(cls.no_access_user)

    @classmethod
    def fill_discrete_parameter_values(cls):
        """
        Fills discrete values for custom parameters
        """
        descriptor_set = cls.parameter_descriptor_set_object.clone()
        descriptor_set.filter_by_category(RootCategoryRecord(project=cls.record_set_object.the_rabbit_project))
        root_discrete = descriptor_set.get_by_alias('root_discrete')
        root_discrete.values.add('grat', "Sine grating")
        root_discrete.values.add('ret', "Retinotopy stimulus")
        root_discrete.values.add('squares', "Squares stimulus")
        root_discrete.values.add('imag', "Images")
        root_discrete.values.add('triang', "Triangles")

    @classmethod
    def _set_user_checkboxes(cls):
        """
        Sets the record checkboxes according to pre-requisites
        """
        record_set = RecordSet()
        user_index = 0
        cls.record_to_user_mapping = defaultdict(lambda: defaultdict(lambda: False))
        for user in cls.full_user, cls.data_full_user, cls.data_view_user, cls.no_access_user:
            record_set.user = user
            record_index = 0
            for record in record_set:
                if record.project.id != cls.working_project.id:
                    continue
                checked = record_index % 4 == user_index
                record.checked = checked
                record.update()
                cls.record_to_user_mapping[record.id][user.id] = checked
                record_index += 1
            user_index += 1

    def setUp(self):
        super().setUp()
        self._container = TestCategory.record_set_object.clone()
        self.container.sort()
        LabjournalCache().flush()

    @parameterized.expand(basic_search_provider())
    def test_basic_search(self, category_cue, token_id, expected_status_code):
        """
        Tries the basic test where no query parameters are provided

        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        self._prepare_records(category_cue, token_id)
        self._test_search(dict(), token_id, expected_status_code)

    @parameterized.expand(date_search_provider())
    def test_date_from_search(self, date_from, date_to, category_cue, token_id, expected_status_code):
        """
        Tests the date and time filter

        :param date_from: a string containing the start date in ISO format
        :param date_to: a string containing the finish date in ISO format
        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        self._prepare_records(category_cue, token_id)
        date_interval = ComplexInterval(-float('inf'), float('inf'))
        query_params = dict()
        if date_from is not None:
            query_params['date_from'] = date_from
            date_from_py = parse(date_from)
            date_interval &= ComplexInterval(date_from_py, float('inf'))
        if date_to is not None:
            query_params['date_to'] = date_to
            date_to_py = parse(date_to)
            date_interval &= ComplexInterval(-float('inf'), date_to_py)
        if date_from is not None or date_to is not None:
            self.container.filter_by_datetime(date_interval)
        self._test_search(query_params, token_id, expected_status_code)

    @parameterized.expand(types_provider())
    def test_type(self, record_types, category_cue, token_id, expected_status_code):
        """
        Tests the 'type' filter in the basic search

        :param record_types: list of types to filter or an invalid filter value
        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        self._prepare_records(category_cue, token_id)
        if isinstance(record_types, list):
            self.container.filter_by_types(record_types)
            query_params = {'type': ','.join([record_type.name for record_type in record_types])}
        else:
            query_params = {'type': record_types}
        self._test_search(query_params, token_id, expected_status_code)

    @parameterized.expand(hashtag_search_provider())
    def test_hashtag_filter(self, hashtag_list, hashtag_logic, category_cue, token_id, expected_status_code):
        """
        Tests the 'hashtags' and 'hashtag_logic' filters.

        :param hashtag_list: list of hashtags that shall be used for the filtration purpose
        :param hashtag_logic: type of the hashtag logic: 'and' or 'or'
        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        processed_hashtag_list, query_params, invalid_hashtag_exists = \
            self._read_hashtag_arguments(hashtag_list, hashtag_logic)
        self._prepare_records(category_cue, token_id)
        if invalid_hashtag_exists and hashtag_logic == 'and':
            self.container.entities.clear()
        elif hashtag_logic in ('and', 'or'):
            self.container.filter_by_hashtag_list(processed_hashtag_list, hashtag_logic)
        self._test_search(query_params, token_id, expected_status_code)

    @parameterized.expand(date_from_hashtags_provider())
    def test_date_hashtags_filter(self,
                                  hashtag_list,
                                  hashtag_logic,
                                  date_from_hashtags,
                                  date_to_hashtags,
                                  category_cue,
                                  token_id,
                                  expected_status_code
                                  ):
        """
        Tests the 'date_from_hashtags' and 'date_to_hashtags' query params

        :param hashtag_list: list of hashtags that shall be used for the filtration purpose
        :param hashtag_logic: type of the hashtag logic: 'and' or 'or'
        :param date_from_hashtags: Minimum number of hours that shall last from the record with a given hashtag
            and the record to show
        :param date_to_hashtags: Maximum number of hours that shall last from the record with a given hashtag and the
            record to show
        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        processed_hashtag_list, query_params, invalid_hashtag_exists = \
            self._read_hashtag_arguments(hashtag_list, hashtag_logic)
        invalid_duration_exists = False
        if isinstance(date_from_hashtags, int):
            date_from_hashtags = timedelta(hours=date_from_hashtags)
            query_params['date_from_hashtags'] = duration_string(date_from_hashtags)
        elif date_from_hashtags is not None:
            query_params['date_from_hashtags'] = date_from_hashtags
            invalid_duration_exists = True
        if isinstance(date_to_hashtags, int):
            date_to_hashtags = timedelta(hours=date_to_hashtags)
            query_params['date_to_hashtags'] = duration_string(date_to_hashtags)
        elif date_to_hashtags is not None:
            query_params['date_to_hashtags'] = date_to_hashtags
            invalid_duration_exists = True
        self._prepare_records(category_cue, token_id)
        auxiliary_container = self.container.clone()
        if invalid_hashtag_exists and hashtag_logic == 'and':
            auxiliary_container.entities.clear()
        elif hashtag_logic in ('and', 'or'):
            auxiliary_container.filter_by_hashtag_list(processed_hashtag_list, hashtag_logic)
        if (date_from_hashtags is None and date_to_hashtags is None) or \
                expected_status_code == status.HTTP_400_BAD_REQUEST:
            pass  # This means that the filter passes everything :-)
        elif len(auxiliary_container) == 0 and date_to_hashtags is not None:  # if no hashtags and cond. (2) appl.
            self.container.entities.clear()
        else:
            assert len(self.container) == 13, "The auxiliary container unexpectedly influences on the main container."
            self.container.filter_by_date_from_records(
                auxiliary_container.entities,
                date_from_hashtags,
                date_to_hashtags
            )
        self._test_search(query_params, token_id, expected_status_code)

    @parameterized.expand(custom_parameter_search_provider())
    def test_custom_parameter_filter(self,
                                     boolean_parameter_filter,
                                     number_parameter_filter,
                                     discrete_parameter_filter,
                                     string_parameter_filter,
                                     filter_logic,
                                     category_cue,
                                     token_id,
                                     expected_status_code
                                     ):
        """
        Tests the 'custom_xxx' and 'logic_custom' filters

        :param boolean_parameter_filter: if not None, filters by a given value of the 'root_boolean' parameter
        :param number_parameter_filter: if not None, filters by a given value of the 'root_num' parameter
        :param discrete_parameter_filter: if not None, filters by a given value of the 'root_discrete' parameter
        :param string_parameter_filter: if not None, filters by a given value of the 'root_string' parameter
        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        self._prepare_records(category_cue, token_id)
        container_filter_parameters = dict()
        query_parameters = dict(logic_custom=filter_logic)
        if expected_status_code == status.HTTP_200_OK:
            container_filter_parameters['_logic'] = getattr(RecordSet.LogicType, filter_logic.upper())
        if boolean_parameter_filter is not None:
            container_filter_parameters['root_bool'] = boolean_parameter_filter
            query_parameters['custom_root_bool'] = str(boolean_parameter_filter)
        if number_parameter_filter is not None:
            container_filter_parameters['root_num'] = number_parameter_filter
            query_parameters['custom_root_num'] = str(number_parameter_filter)
        if discrete_parameter_filter is not None:
            container_filter_parameters['root_discrete'] = discrete_parameter_filter
            query_parameters['custom_root_discrete'] = str(discrete_parameter_filter)
        if string_parameter_filter is not None:
            container_filter_parameters['root_string'] = string_parameter_filter
            query_parameters['custom_root_string'] = str(string_parameter_filter)
        if expected_status_code == status.HTTP_200_OK:
            self.container.filter_by_custom_parameters(container_filter_parameters)
        self._test_search(query_parameters, token_id, expected_status_code)

    @parameterized.expand(logic_provider())
    def test_bad_custom_parameter_filter_and_request(self, operation):
        self._prepare_records('/a', 'full')
        if operation == 'and':
            self.container.entities.clear()
        else:
            self.container.filter_by_custom_parameters({'root_bool': True, '_logic': RecordSet.LogicType.OR})
        self._test_search(
            {'custom_root_bool': True, 'custom_xxx': 'xxx', 'logic_custom': operation},
            'full',
            status.HTTP_200_OK,
        )

    @parameterized.expand(relative_date_search_provider())
    def test_relative_date_search(self, date_from, date_to, category_cue, token_id, expected_status_code):
        """
        Tests the 'date_from_relative' and 'date_to_relative' search parameters.

        :param date_from: the duration from start of the parent category
        :param date_to: the duration of finish to the parent category
        :param category_cue: some short string that identifies the category
        :param token_id: ID of a token to use
        :param expected_status_code: status code to be expected
        """
        self._prepare_records(category_cue, token_id)
        if expected_status_code == status.HTTP_200_OK:
            date_from_for_filter = None
            date_to_for_filter = None
            first_record_datetime = None
            for entity in self.container:
                if entity.datetime is not None:
                    first_record_datetime = entity.datetime
                    break
            if isinstance(date_from, timedelta):
                date_from_for_filter = date_from + first_record_datetime
            if isinstance(date_to, timedelta):
                date_to_for_filter = date_to + first_record_datetime
            if date_from_for_filter is not None and date_to_for_filter is not None:
                try:
                    complex_interval = ComplexInterval(date_from_for_filter, date_to_for_filter)
                except ValueError:
                    complex_interval = ComplexInterval(-float('inf'), float('inf'), contains=False)
            elif date_from_for_filter is not None and date_to_for_filter is None:
                complex_interval = ComplexInterval(date_from_for_filter, float('inf'))
            elif date_from_for_filter is None and date_to_for_filter is not None:
                complex_interval = ComplexInterval(-float('inf'), date_to_for_filter)
            else:
                complex_interval = ComplexInterval(-float('inf'), float('inf'))
            self.container.filter_by_datetime(complex_interval)
        if isinstance(date_from, timedelta):
            date_from = duration_string(date_from)
        if isinstance(date_to, timedelta):
            date_to = duration_string(date_to)
        query_params = dict()
        if date_from is not None:
            query_params['date_from_relative'] = date_from
        if date_to is not None:
            query_params['date_to_relative'] = date_to
        self._test_search(query_params, token_id, expected_status_code)

    @parameterized.expand(name_provider)
    def test_name_search(self, record_name):
        """
        Tests records by their name

        :param record_name: the query string to test
        """
        self._prepare_records('/a', 'full')
        self.container.filter_by_name(record_name)
        query_params = {'name': record_name}
        self._test_search(query_params, 'full', status.HTTP_200_OK)

    def print_users_and_projects(self):
        """
        Prints detailed information about users and projects
        """
        print("Users:")
        for user, token in [
            (self.full_user, self.full_token),
            (self.data_full_user, self.data_full_token),
            (self.data_view_user, self.data_view_token),
            (self.no_access_user, self.no_access_token),
        ]:
            print("%d\t%s\t%20s\t%s" % (user.id, user.login, "%s %s" % (user.name, user.surname), token))
        print("Records:")
        for record in self.container:
            if record.project.id != self.working_project.id:
                continue
            if record.datetime is None:
                record_time = "n/a"
            else:
                record_time = record.datetime.isoformat()
            print("%s\t%10s\t%19s\t%8s\t" % (
                record.id,
                record.path if record.type != LabjournalRecordType.service else '-',
                record_time,
                record.type.name
            ), end="")
            print("%s\t%s\t%s\t%s\t" % (
                self.record_to_user_mapping[record.id][self.full_user.id],
                self.record_to_user_mapping[record.id][self.data_full_user.id],
                self.record_to_user_mapping[record.id][self.data_view_user.id],
                self.record_to_user_mapping[record.id][self.no_access_user.id],
            ), end="")
            if hasattr(record, 'alias'):
                print("%18s\t" % record.alias, end="")
            if hasattr(record, 'name'):
                print("%18s\t" % record.name, end="")
            hashtags = ", ".join([hashtag.description for hashtag in record.hashtags])
            print("%29s\t" % hashtags, end="")
            print("%d\t" % len(record.customparameters), end="")
            if 'root_bool' in record.customparameters:
                print(
                    record.custom_root_bool,
                    record.custom_root_num,
                    record.custom_root_discrete,
                    record.custom_root_string,
                    end="",
                )
            print("")

    def assert_items_equal(self, actual_item, desired_item):
        """
        Compares two list item

        :param actual_item: the item received within the response
        :param desired_item: the item taken from the container
        :return: nothing
        """
        desired_item = RecordSet().get(desired_item.id)
        self.assertEquals(actual_item['id'], desired_item.id, "Item IDs are not equal")
        if isinstance(desired_item, ServiceRecord):
            self.assertNotIn('alias', actual_item, "Service records don't have any alias")
            self.assertNotIn('path', actual_item, "Service records don't have any path")
            self.assertEquals(actual_item['name'], desired_item.name, "Item names are not equal")
        else:
            self.assertEquals(actual_item['alias'], desired_item.alias, "Item aliases are not equal")
            self.assertEquals(actual_item['path'], desired_item.path, "Item paths are not equal")
            self.assertNotIn('name', actual_item, "Only service records have name")
        record_time = actual_item['datetime']
        if record_time is not None:
            record_time = make_naive(parse(record_time))
        self.assertEquals(record_time, desired_item.datetime, "Record date and time mismatch")
        relative_time = actual_item['relative_time']
        if relative_time is not None:
            relative_time = parse_duration(relative_time)
        self.assertEquals(relative_time, desired_item.relative_time, "Relative time mismatch")
        self.assertEquals(
            actual_item['checked'],
            self.record_to_user_mapping[desired_item.id][self._authorized_user.id],
            "Bad check status",
        )
        self.assertEquals(actual_item['type'], desired_item.type.name, "Record type mismatch")
        if isinstance(desired_item, CategoryRecord):
            finish_time = actual_item['finish_time']
            if finish_time is not None:
                finish_time = make_naive(parse(finish_time))
            self.assertEquals(finish_time, desired_item.finish_time, "Finish time mismatch")
            self.assertEquals(actual_item['base_directory'], desired_item.base_directory, "Base directory mismatch")
        else:
            self.assertNotIn('finish_time', actual_item,
                             "The finish time shall be present in categories only")
            self.assertNotIn('base_directory', actual_item,
                             "Base directory shall be defined for categories only")
        self.assertEquals(actual_item['comments'], desired_item.comments, "Record comments mismatch")
        custom_parameters = set()
        for parameter_name, parameter_value in desired_item.customparameters.items():
            full_parameter_name = "custom_%s" % parameter_name
            self.assertIn(full_parameter_name, actual_item,
                          "The custom parameter was not present in the output response")
            self.assertEquals(actual_item[full_parameter_name], parameter_value, "Bad value of custom parameter")
            custom_parameters.add(full_parameter_name)
        actual_custom_parameters = {
            key for key in actual_item.keys()
            if key.startswith('custom_')
        }
        self.assertEquals(actual_custom_parameters, custom_parameters,
                          "Some custom parameters are present in the response output but absent in the entity")

    def _get_page_data(self, response):
        """
        Returns part of the response data that contains a single Django REST Framework page

        :param response: the response
        :return: value of a field that contains a single Django REST Framework page
        """
        return response.data['records']

    def _prepare_records(self, category_cue, token_id):
        """
        Prepares test environment for a given particular test case

        :param category_cue: a cue for the parent category
        :param token_id: ID pf a user that should be authorized
        """
        if category_cue is None:
            category = RootCategoryRecord(project=self.working_project)
            self._request_path = "/api/%s/projects/the_rabbit_project/labjournal/categories/" % self.API_VERSION
        elif category_cue.startswith("/"):
            category = RecordSet().get((self.working_project, category_cue))
            self._request_path = \
                "/api/%s/projects/the_rabbit_project/labjournal/categories%s/" % (self.API_VERSION, category_cue)
        else:
            if category_cue.find(":") != -1:
                project_cue, category_cue = category_cue.split(":")
            else:
                project_cue = "the_rabbit_project"
            category = RecordSet().get((self.working_project, "/" + category_cue))
            self._request_path = \
                "/api/%s/projects/%s/labjournal/categories/%s/" % (self.API_VERSION, project_cue, category.id)
        self._authorized_user = getattr(self, token_id + "_user")
        self.container.filter_by_parent_category(category)
        self.container.filter_by_project(self.working_project)
        return category

    def _read_hashtag_arguments(self, hashtag_list, hashtag_logic):
        """
        Reads the hashtag list and the hashtag logic from the test arguments

        :param hashtag_list: list of hashtags as given by the data provider
        :param hashtag_logic: the hashtag logic as given by the data provider
        :return: a tuple containing the following variables:
            processed_hashtag_list - list of all valid hashtags to be filtered by the RecordSetObject
            query_params - Query parameters to be put into the HTTP request for an endpoint to test
            invalid_hashtag_exists - True if the test case gives at least one invalid hashtag inside the hashtag list,
                False if the test case implies that all hashtags are valid
        """
        processed_hashtag_list = list()
        invalid_hashtag_exists = False
        hashtag_list_for_request = list()
        hashtag_set_object = self.record_hashtag_set_object.clone()
        hashtag_set_object.filter_by_project(self.working_project)
        for hashtag_cue in hashtag_list:
            if hashtag_cue in ["шахматный", "редкий", "редчайший"]:
                hashtag = hashtag_set_object.get_by_alias(hashtag_cue)
                processed_hashtag_list.append(hashtag)
                hashtag_list_for_request.append(str(hashtag.id))
            elif hashtag_cue == 'invalid':
                bad_hashtag_id = LabjournalHashtag.objects.all().aggregate(max_id=Max('id'))['max_id'] + 1
                invalid_hashtag_exists = True
                hashtag_list_for_request.append(str(bad_hashtag_id))
            else:
                invalid_hashtag_exists = True
                hashtag_list_for_request.append(hashtag_cue)
        hashtag_list_for_request = ",".join(hashtag_list_for_request)
        query_params = {
            'hashtags': hashtag_list_for_request,
            'hashtag_logic': hashtag_logic,
        }
        return processed_hashtag_list, query_params, invalid_hashtag_exists
