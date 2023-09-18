import unittest
from pymongo import MongoClient
import config
import sys

from event.event_repository import EventRepository


class TestEventRepository(unittest.TestCase):
    def setUp(self):
        self.client = MongoClient('localhost', 27017)
        self.db_name = config.TestConfig.DB_NAME
        self.db = self.client[self.db_name]
        self.repository = EventRepository()
        self.event_data = {
            '_id': '1',
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
        self.client.drop_database(self.db_name)
        self.client.close()

    def test_get_events_empty(self):
        events = self.repository.get_events()
        self.assertEqual(len(events.distinct('_id')), 0)

    def test_get_events_full(self):
        self.db.events.insert_one(self.event_data)
        events = self.repository.get_events()
        self.assertEqual(len(events.distinct('_id')), 1)
        self.assertEqual(events[0], self.event_data)

    def test_get_event_by_id_empty(self):
        event = self.repository.get_event_by_id('1')
        self.assertIsNone(event)

    def test_get_event_by_id_full(self):
        self.db.events.insert_one(self.event_data)
        event = self.repository.get_event_by_id('1')
        self.assertEqual(event, self.event_data)

    def test_get_event_by_event_id_empty(self):
        event = self.repository.get_event_by_event_id(1)
        self.assertIsNone(event)

    def test_get_event_by_event_id_full(self):
        self.db.events.insert_one(self.event_data)
        event = self.repository.get_event_by_event_id(1)
        self.assertEqual(event, self.event_data)
