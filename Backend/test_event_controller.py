import json
import os
import unittest
from unittest.mock import Mock

from flask import Flask

from event import event_controller
from method_return import Success, Failure


class TestEventController(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.controller = event_controller.EventController()
        self.mock_service = Mock()
        self.controller.service = self.mock_service
        self.app.register_blueprint(self.controller.event_blueprint, url_prefix='/')
        self.client = self.app.test_client()
        self.path = os.path.join(os.path.expanduser('~'), "path.json")
        self.path1 = os.path.join(os.path.expanduser('~'), "path1.json")

        self.event = {
            'eventId': 1,
            'timestamp': 1,
            'fromVisit': 0,
            'title': 'Page Visit',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True,
            '_id': '1'
        }

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        if os.path.exists(self.path1):
            os.remove(self.path1)

    def test_get_database_failure(self):
        self.mock_service.get_database.return_value = Success(self.path1)
        response = self.client.get('/database')
        self.assertEqual(response.status_code, 500)

    def test_get_database_success(self):
        with open(self.path, 'w'):
            pass
        self.mock_service.get_database.return_value = Success(self.path)
        response = self.client.get('/database')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.headers['Content-Type'])

    def test_get_events_empty(self):
        self.mock_service.get_events.return_value = Success([])
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_events_full(self):
        self.mock_service.get_events.return_value = Success([self.event])
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.event])

    def test_post_events(self):
        self.mock_service.post_events.return_value = Success(self.event)
        response = self.client.post('/send', data=json.dumps(self.event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_event_by_id_empty(self):
        self.mock_service.get_event_by_id.return_value = Failure("No event with given _id was found.")
        response = self.client.get('/event/1')
        self.assertEqual(response.status_code, 404)

    def test_get_event_by_id_full(self):
        self.mock_service.get_event_by_id.return_value = Success(self.event)
        response = self.client.get('/event/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_event_by_event_id_empty(self):
        self.mock_service.get_event_by_event_id.return_value = Failure("No event with given eventId was found.")
        response = self.client.get('/eventId/1')
        self.assertEqual(response.status_code, 404)

    def test_get_event_by_event_id_full(self):
        self.mock_service.get_event_by_event_id.return_value = Success(self.event)
        response = self.client.get('/eventId/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_eventlog_empty(self):
        self.mock_service.get_eventlog.return_value = Success([])
        response = self.client.get('/eventlog')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_eventlog_full(self):
        self.mock_service.get_eventlog.return_value = Success([[self.event]])
        response = self.client.get('/eventlog')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [[self.event]])

    def test_get_xes_empty(self):
        self.mock_service.get_xes.return_value = Success(self.path1)
        response = self.client.get('/xes')
        self.assertEqual(response.status_code, 500)

    def test_get_xes_full(self):
        with open(self.path, 'w'):
            pass
        self.mock_service.get_xes.return_value = Success(self.path)
        response = self.client.get('/xes')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response.headers['Content-Type'])

    def test_get_image_empty(self):
        self.mock_service.get_image.return_value = Success(self.path1)
        response = self.client.get('/image')
        self.assertEqual(response.status_code, 500)

    def test_get_image_full(self):
        with open(self.path, 'w'):
            pass
        self.mock_service.get_image.return_value = Success(self.path)
        response = self.client.get('/image')
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/png', response.headers['Content-Type'])
