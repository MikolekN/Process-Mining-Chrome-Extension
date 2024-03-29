import json
import os
from copy import deepcopy
from unittest import TestCase

from flask import Flask

import config
from event import event_controller


class EventControllerTestCase(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        controller = event_controller.EventController(testing=True)
        self.app.register_blueprint(controller.event_blueprint, url_prefix='/')
        self.client = self.app.test_client()

        db_name = config.TestConfig.DB_NAME
        home_directory = os.path.expanduser('~')
        self.db = os.path.join(home_directory, db_name + ".json")

        self.event = {
            '_id': '64df4cf73595073f910c378d',
            'eventId': 1,
            'timestamp': 1,
            'fromVisit': 0,
            'title': 'Test Event',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True
        }

    def tearDown(self):
        os.remove(self.db)

    def test_get_database_empty(self):
        response = self.client.get('/database')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_database_one_event(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/database')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_database_full(self):
        with open(self.db, 'w') as file:
            json.dump([self.event, self.event], file)
        response = self.client.get('/database')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.event, self.event])

    def test_get_events_empty(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_events_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.event])

    def test_post_events(self):
        response = self.client.post('/send', data=json.dumps(self.event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        received_event = response.json
        expected_event = deepcopy(self.event)
        expected_event['_id'] = received_event['_id']
        self.assertEqual(received_event, expected_event)

    def test_post_events_event_already_exists(self):
        self.client.post('/send', data=json.dumps(self.event), content_type='application/json')
        response = self.client.post('/send', data=json.dumps(self.event), content_type='application/json')
        self.assertEqual(response.status_code, 500)

    def test_get_event_by_id_empty(self):
        response = self.client.get('/event/64df4cf73595073f910c378d')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, "No event with given _id was found.")

    def test_get_event_by_id_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/event/64df4cf73595073f910c378d')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_event_by_event_id_empty(self):
        response = self.client.get('/eventId/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, "No event with given eventId was found.")

    def test_get_event_by_event_id_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/eventId/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.event)

    def test_get_eventlog_empty(self):
        response = self.client.get('/eventlog')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.headers['Content-Type'])
        self.assertEqual(response.json, [])

    def test_get_eventlog_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/eventlog')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.headers['Content-Type'])
        self.assertEqual(response.json, [[self.event]])

    def test_get_xes_empty(self):
        response = self.client.get('/xes')
        self.assertEqual(response.status_code, 500)

    def test_get_xes_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/xes')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response.headers['Content-Type'])

    def test_get_image_empty(self):
        response = self.client.get('/image')
        self.assertEqual(response.status_code, 500)

    def test_get_image_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.client.get('/image')
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/png', response.headers['Content-Type'])
