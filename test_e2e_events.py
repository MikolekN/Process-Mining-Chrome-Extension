import unittest
from unittest import TestCase
from unittest.mock import Mock

from bson import ObjectId
from pymongo import MongoClient
from flask import Flask

import config
from event.event_controller import event_blueprint


class EventControllerTestCase(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(event_blueprint, url_prefix='/events')
        self.client = self.app.test_client()

        self.db_client = MongoClient('localhost', 27017)
        self.db_name = config.TestConfig.DB_NAME
        self.db = self.db_client[self.db_name]

        self.event_save_data = {
            '_id': ObjectId('64df4cf73595073f910c378d'),
            '_ownerId': ObjectId('64fefba26477d407afbc6bca'),
            'eventId': 1,
            'timestamp': '2023-07-18',
            'fromVisit': 0,
            'title': 'Test Event',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True
        }
        self.expected_received_data = {
            '_id': '64df4cf73595073f910c378d',
            '_ownerId': '64fefba26477d407afbc6bca',
            'eventId': 1,
            'timestamp': '2023-07-18',
            'fromVisit': 0,
            'title': 'Test Event',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True
        }

    def tearDown(self):
        self.db_client.drop_database(self.db_name)
        self.db_client.close()

    def test_get_events_empty(self):
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_events_full(self):
        self.db.events.insert_one(self.event_save_data)
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [self.expected_received_data])

    def test_get_event_by_id_empty(self):
        response = self.client.get('/events/event/64df4cf73595073f910c378d')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'message': 'Event not found'})

    def test_get_event_by_id_full(self):
        self.db.events.insert_one(self.event_save_data)
        response = self.client.get('/events/event/64df4cf73595073f910c378d')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.expected_received_data)

    def test_get_event_by_event_id_empty(self):
        response = self.client.get('/events/eventId/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {'message': 'Event not found'})

    def test_get_event_by_event_id_full(self):
        self.db.events.insert_one(self.event_save_data)
        response = self.client.get('/events/eventId/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, self.expected_received_data)
