import json
import os
import unittest
from copy import deepcopy

import config
from event.event_repository import EventRepository


class TestEventRepository(unittest.TestCase):
    def setUp(self):
        db_name = config.TestConfig.DB_NAME
        home_directory = os.path.expanduser('~')
        self.db = os.path.join(home_directory, db_name + ".json")

        self.repository = EventRepository(testing=True)

        self.event = {
            '_id': '1',
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

    def test_get_database(self):
        response = self.repository.get_database()
        self.assertTrue(response.ok)
        self.assertEqual(response.data, self.db)

    def test_get_events_empty(self):
        response = self.repository.get_events()
        self.assertTrue(response.ok)
        self.assertEqual(len(response.data), 0)

    def test_get_events_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.repository.get_events()
        self.assertTrue(response.ok)
        events = response.data
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], self.event)

    def test_post_events_event_already_exists(self):
        self.repository.post_events(self.event)
        response = self.repository.post_events(self.event)
        self.assertFalse(response.ok)

    def test_post_events(self):
        response = self.repository.post_events(self.event)
        self.assertTrue(response.ok)
        expected_event = deepcopy(self.event)
        expected_event['_id'] = response.data['_id']
        self.assertEqual(response.data, self.event)

    def test_get_event_by_id_empty(self):
        response = self.repository.get_event_by_id('1')
        self.assertFalse(response.ok)
        self.assertEqual(response.message, "No event with given _id was found.")

    def test_get_event_by_id_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.repository.get_event_by_id('1')
        self.assertTrue(response.ok)
        self.assertEqual(response.data, self.event)

    def test_get_event_by_event_id_empty(self):
        response = self.repository.get_event_by_event_id(1)
        self.assertFalse(response.ok)
        self.assertEqual(response.message, "No event with given eventId was found.")

    def test_get_event_by_event_id_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        response = self.repository.get_event_by_event_id(1)
        self.assertTrue(response.ok)
        self.assertEqual(response.data, self.event)
