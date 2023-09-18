import unittest
from unittest.mock import Mock
from event.event_service import EventService
from method_return import Success


class TestEventService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = Mock()
        self.event_service = EventService()
        self.event_service.repository = self.mock_repository

    def test_get_events_empty(self):
        mock_events = []
        self.mock_repository.get_events.return_value = mock_events
        result = self.event_service.get_events()
        self.assertEqual(result, mock_events)

    def test_get_events_full(self):
        mock_events = [
            {'_id': '1', 'eventId': 1, 'timestamp': '2023-07-18', 'fromVisit': 0, 'title': 'Event 1',
             'url': 'http://example.com', 'transition': 'click', 'duration': 10, 'tip': True},
            {'_id': '2', 'eventId': 2, 'timestamp': '2023-07-19', 'fromVisit': 1, 'title': 'Event 2',
             'url': 'http://example.com', 'transition': 'click', 'duration': 15, 'tip': False},
        ]
        self.mock_repository.get_events.return_value = mock_events
        result = self.event_service.get_events()
        self.assertEqual(result, mock_events)

    def test_validate_event_missing_key(self):
        mock_event = {'timestamp': '2023-07-18', 'fromVisit': 0, 'title': 'Event 1',
                      'url': 'http://example.com', 'transition': 'click', 'duration': 10, 'tip': True}
        result = self.event_service.validate_data(mock_event)
        self.assertEqual(result.ok, False)
        self.assertIsNotNone(result.message)

    def test_validate_event_additional_key(self):
        expected_event = {'eventId': 1, 'timestamp': '2023-07-18', 'fromVisit': 0, 'title': 'Event 1',
                          'url': 'http://example.com', 'transition': 'click', 'duration': 10, 'tip': True}
        mock_event = {'eventId': 1, 'timestamp': '2023-07-18', 'fromVisit': 0, 'title': 'Event 1',
                      'url': 'http://example.com', 'transition': 'click', 'duration': 10, 'tip': True, 'new': "NEW"}
        result = self.event_service.validate_data(mock_event)
        self.assertEqual(result.ok, True)
        self.assertEqual(result.data, expected_event)

    def test_post_events(self):
        mock_event = {'eventId': 1, 'timestamp': '2023-07-18', 'fromVisit': 0, 'title': 'Event 1',
                      'url': 'http://example.com', 'transition': 'click', 'duration': 10, 'tip': True}
        self.mock_repository.post_events.return_value = Success(1)
        result = self.event_service.post_events(mock_event)
        self.assertEqual(result.ok, True)

    def test_get_event_by_id_empty(self):
        mock_event = None
        self.mock_repository.get_event_by_id.return_value = mock_event
        result = self.event_service.get_event_by_id('64df4cf73595073f910c378d')
        self.assertEqual(result, mock_event)

    def test_get_event_by_id_full(self):
        mock_event = {'_id': '64df4cf73595073f910c378d', 'eventId': 1, 'timestamp': '2023-07-18',
                      'fromVisit': 0, 'title': 'Event 1', 'url': 'http://example.com', 'transition': 'click',
                      'duration': 10, 'tip': True}
        self.mock_repository.get_event_by_id.return_value = mock_event
        result = self.event_service.get_event_by_id('64df4cf73595073f910c378d')
        self.assertEqual(result, mock_event)

    def test_get_event_by_event_id_empty(self):
        mock_event = None
        self.mock_repository.get_event_by_event_id.return_value = mock_event
        result = self.event_service.get_event_by_event_id(1)
        self.assertEqual(result, mock_event)

    def test_get_event_by_event_id_full(self):
        mock_event = {'_id': '1', 'eventId': 1, 'timestamp': '2023-07-18', 'fromVisit': 0,
                      'title': 'Event 1', 'url': 'http://example.com', 'transition': 'click', 'duration': 10,
                      'tip': True}
        self.mock_repository.get_event_by_event_id.return_value = mock_event
        result = self.event_service.get_event_by_event_id(1)
        self.assertEqual(result, mock_event)
