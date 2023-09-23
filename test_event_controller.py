import json
import unittest
from unittest.mock import Mock

from flask import Flask

from event import event_controller
from method_return import Success


class TestEventController(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.controller = event_controller.EventController()
        self.mock_service = Mock()
        self.controller.service = self.mock_service
        self.app.register_blueprint(self.controller.event_blueprint, url_prefix='/')
        self.client = self.app.test_client()

        self.event = {
            'eventId': 1,
            'timestamp': '2023-07-18',
            'fromVisit': 0,
            'title': 'Page Visit',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True,
            '_id': '1'
        }

    def test_get_events_empty(self):
        self.mock_service.get_events.return_value = []
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_events_full(self):
        self.mock_service.get_events.return_value = [self.event]
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.event])

    def test_post_events(self):
        self.mock_service.post_events.return_value = Success(self.event)
        response = self.client.post('/', data=json.dumps(self.event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_event_by_id_empty(self):
        self.mock_service.get_event_by_id.return_value = None
        response = self.client.get('/event/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'message': 'Event not found'})

    def test_get_event_by_id_full(self):
        self.mock_service.get_event_by_id.return_value = self.event
        response = self.client.get('/event/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_event_by_event_id_empty(self):
        self.mock_service.get_event_by_event_id.return_value = None
        response = self.client.get('/eventId/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'message': 'Event not found'})

    def test_get_event_by_event_id_full(self):
        self.mock_service.get_event_by_event_id.return_value = self.event
        response = self.client.get('/eventId/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)
