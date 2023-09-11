import unittest
from flask import Flask, request, jsonify
from unittest.mock import Mock, patch

from event.event_controller import event_blueprint
from event.event_service import EventService


class TestEventController(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(event_blueprint, url_prefix='/events')
        self.client = self.app.test_client()
        self.event_service = Mock()
        self.patcher = patch('event.event_controller.event_service', autospec=True)
        self.event = {
            'eventId': 1,
            'timestamp': '2023-07-18',
            'fromVisit': 0,
            'title': 'Page Visit',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True,
            '_ownerId': '1',
            '_id': '1'
        }

    def test_get_events_empty(self):
        with patch('event.event_controller.event_service', autospec=True) as mock_service:
            mock_service.get_events.return_value = []

            response = self.client.get('/events')
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, [])

    def test_get_events_full(self):
        with patch('event.event_controller.event_service', autospec=True) as mock_service:
            mock_service.get_events.return_value = [self.event]

            response = self.client.get('/events')
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, [self.event])

    def test_get_event_by_id_empty(self):
        with patch('event.event_controller.event_service', autospec=True) as mock_service:
            mock_service.get_event_by_id.return_value = None

            response = self.client.get('/events/event/1')
            data = response.get_json()

            self.assertEqual(response.status_code, 404)
            self.assertEqual(data, {'message': 'Event not found'})

    def test_get_event_by_id_full(self):
        with patch('event.event_controller.event_service', autospec=True) as mock_service:
            mock_service.get_event_by_id.return_value = self.event

            response = self.client.get('/events/event/1')
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, self.event)

    def test_get_event_by_event_id_empty(self):
        with patch('event.event_controller.event_service', autospec=True) as mock_service:
            mock_service.get_event_by_event_id.return_value = None

            response = self.client.get('/events/eventId/1')
            data = response.get_json()

            self.assertEqual(response.status_code, 404)
            self.assertEqual(data, {'message': 'Event not found'})

    def test_get_event_by_event_id_full(self):
        with patch('event.event_controller.event_service', autospec=True) as mock_service:
            mock_service.get_event_by_event_id.return_value = self.event

            response = self.client.get('/events/eventId/1')
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, self.event)
