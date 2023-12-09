import unittest
from unittest.mock import Mock

from event.event_service import EventService, validate_data, validate_date_data
from method_return import Success, Failure


class TestEventService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.event_service = EventService()
        self.event_service.repository = self.mock_repository
        self.event1 = {'_id': '1', 'eventId': 1, 'timestamp': 1, 'fromVisit': 0, 'title': 'Event 1',
                       'url': 'http://example.com', 'transition': 'click', 'duration': 10, 'tip': True}
        self.event2 = {'_id': '2', 'eventId': 2, 'timestamp': 1, 'fromVisit': 1, 'title': 'Event 2',
                       'url': 'http://example.com', 'transition': 'click', 'duration': 15, 'tip': False}
        self.event3 = {'_id': '2', 'eventId': 2, 'timestamp': 100000000, 'fromVisit': 1, 'title': 'Event 2',
                       'url': 'http://example.com', 'transition': 'click', 'duration': 0, 'tip': False}

    def test_validate_data_missing_keys(self):
        data = {}
        result = validate_data(data)
        self.assertFalse(result.ok)

    def test_validate_data_additional_keys(self):
        data = {'eventId': 1,
                'timestamp': 1,
                'fromVisit': 1,
                'title': 1,
                'url': 1,
                'transition': 1,
                'duration': 1,
                'tip': 1}
        data2 = {'eventId': 1,
                 'timestamp': 1,
                 'fromVisit': 1,
                 'title': 1,
                 'url': 1,
                 'transition': 1,
                 'duration': 1,
                 'tip': 1,
                 'hallo': 1}
        result = validate_data(data2)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, data)

    def test_validate_data_success(self):
        data = {'eventId': 1,
                'timestamp': 1,
                'fromVisit': 1,
                'title': 1,
                'url': 1,
                'transition': 1,
                'duration': 1,
                'tip': 1}
        result = validate_data(data)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, data)

    def test_validate_date_data_additional_keys(self):
        data = {'startDate': 1,
                'endDate': 1}
        data2 = {'startDate': 1,
                 'endDate': 1,
                 'hallo': 1}
        result = validate_date_data(data2)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, data)

    def test_validate_date_data_empty(self):
        data = {'endDate': None, 'startDate': None}
        data2 = {}
        result = validate_date_data(data2)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, data)

    def test_validate_date_data_success(self):
        data = {'endDate': 1, 'startDate': 1}
        result = validate_date_data(data)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, data)

    def test_get_database_empty(self):
        mock_events = []
        self.mock_repository.get_database.return_value = Success(mock_events)
        result = self.event_service.get_database()
        self.assertEqual(result.data, mock_events)

    def test_get_database_full(self):
        mock_events = [self.event1, self.event2]
        self.mock_repository.get_database.return_value = Success(mock_events)
        result = self.event_service.get_database()
        self.assertEqual(result.data, mock_events)

    def test_get_events_empty(self):
        mock_events = []
        self.mock_repository.get_events.return_value = Success(mock_events)
        result = self.event_service.get_events({})
        self.assertEqual(result.data, mock_events)

    def test_get_events_full(self):
        mock_events = [self.event1, self.event2]
        self.mock_repository.get_events.return_value = Success(mock_events)
        result = self.event_service.get_events({})
        self.assertEqual(result.data, mock_events)

    def test_filter_json_event(self):
        data = [self.event1, self.event2]
        data2 = [self.event1, self.event2, self.event3]
        self.event_service.filter_value = 0
        result = self.event_service.filter_json_events(data2)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, data)

    def test_set_filter_empty(self):
        data = []
        result = self.event_service.set_filter(data)
        self.assertTrue(result.ok)
        self.assertEqual(self.event_service.filter_value, 0)

    def test_set_filter_full_0(self):
        data = [self.event1, self.event2]
        result = self.event_service.set_filter(data)
        self.assertTrue(result.ok)
        self.assertEqual(self.event_service.filter_value, 0)

    def test_set_filter_full(self):
        data = [self.event2, self.event3]
        result = self.event_service.set_filter(data)
        self.assertTrue(result.ok)
        self.assertEqual(self.event_service.filter_value, 80)

    def test_set_date_empty(self):
        data = {'endDate': None, 'startDate': None}
        result = self.event_service.set_date(data)
        self.assertTrue(result.ok)
        self.assertIsNone(self.event_service.start_date)
        self.assertIsNone(self.event_service.end_date)

    def test_set_date_full(self):
        data = {'endDate': "2001-07-01", 'startDate': "2001-07-01"}
        result = self.event_service.set_date(data)
        self.assertTrue(result.ok)
        self.assertEqual(self.event_service.start_date, "2001-07-01")
        self.assertEqual(self.event_service.end_date, "2001-07-01")

    def test_post_events_event_already_exists(self):
        self.mock_repository.post_events.return_value = Failure(None)
        result = self.event_service.post_events(self.event1)
        self.assertFalse(result.ok)

    def test_post_events(self):
        self.mock_repository.post_events.return_value = Success(self.event1)
        result = self.event_service.post_events(self.event1)
        self.assertEqual(result.ok, True)
        self.assertEqual(result.data, self.event1)

    def test_get_event_by_id_empty(self):
        self.mock_repository.get_event_by_id.return_value = Failure(None)
        result = self.event_service.get_event_by_id('64df4cf73595073f910c378d')
        self.assertFalse(result.ok)

    def test_get_event_by_id_full(self):
        mock_event = {'_id': '64df4cf73595073f910c378d', 'eventId': 1, 'timestamp': 1,
                      'fromVisit': 0, 'title': 'Event 1', 'url': 'http://example.com', 'transition': 'click',
                      'duration': 10, 'tip': True}
        self.mock_repository.get_event_by_id.return_value = mock_event
        result = self.event_service.get_event_by_id('64df4cf73595073f910c378d')
        self.assertEqual(result, mock_event)

    def test_get_event_by_event_id_empty(self):
        self.mock_repository.get_event_by_event_id.return_value = Failure(None)
        result = self.event_service.get_event_by_event_id(1)
        self.assertFalse(result.ok)

    def test_get_event_by_event_id_full(self):
        mock_event = {'_id': '1', 'eventId': 1, 'timestamp': 1, 'fromVisit': 0,
                      'title': 'Event 1', 'url': 'http://example.com', 'transition': 'click', 'duration': 10,
                      'tip': True}
        self.mock_repository.get_event_by_event_id.return_value = Success(mock_event)
        result = self.event_service.get_event_by_event_id(1)
        self.assertTrue(result.ok)
        self.assertEqual(result.data, mock_event)
