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
            'timestamp': '2023-07-18',
            'fromVisit': 0,
            'title': 'Test Event',
            'url': 'http://example.com',
            'transition': 'click',
            'duration': 10,
            'tip': True
        }

    def tearDown(self):
        os.remove(self.db)

    def test_get_events_empty(self):
        events = self.repository.get_events()
        self.assertEqual(len(events), 0)

    def test_get_events_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        events = self.repository.get_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], self.event)

    def test_post_events(self):
        result = self.repository.post_events(self.event)
        self.assertEqual(result.ok, True)
        expected_event = deepcopy(self.event)
        expected_event['_id'] = result.data['_id']
        self.assertEqual(result.data, self.event)

    def test_get_event_by_id_empty(self):
        event = self.repository.get_event_by_id('1')
        self.assertIsNone(event)

    def test_get_event_by_id_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        event = self.repository.get_event_by_id('1')
        self.assertEqual(event, self.event)

    def test_get_event_by_event_id_empty(self):
        event = self.repository.get_event_by_event_id(1)
        self.assertIsNone(event)

    def test_get_event_by_event_id_full(self):
        with open(self.db, 'w') as file:
            json.dump(self.event, file)
        event = self.repository.get_event_by_event_id(1)
        self.assertEqual(event, self.event)
