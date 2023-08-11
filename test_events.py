import unittest
from events import Event, Events


class TestEvent(unittest.TestCase):
    def test_event_creation(self):
        event = Event(event_id=1, timestamp="2023-07-19", from_visit=0, title="Visit 1", url="https://example.com", transition="link", duration=10)
        self.assertEqual(event.event_id, 1)
        self.assertEqual(event.timestamp, "2023-07-19")
        self.assertEqual(event.from_visit, 0)
        self.assertEqual(event.title, "Visit 1")
        self.assertEqual(event.url, "https://example.com")
        self.assertEqual(event.transition, "link")
        self.assertEqual(event.duration, 10)


class TestEvents(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.event1 = Event(1, "2023-07-19", 0, "Visit 1", "https://example.com", "link", 10)
        cls.event2 = Event(2, "2023-07-20", 1, "Visit 2", "https://example.com/page", "link", 5)
        cls.event3 = Event(3, "2023-07-21", 2, "Visit 3", "https://example.com/page/page", "link", 0)

    def test_empty_events(self):
        events_list = Events()
        self.assertEqual(len(events_list.events), 0)

    def test_initial_events_single(self):
        events_list = Events(self.event1)
        self.assertEqual(len(events_list.events), 1)
        self.assertEqual(events_list.events[0], self.event1)

    def test_initial_events_list(self):
        events_list = Events([self.event1, self.event2])
        self.assertEqual(len(events_list.events), 2)
        self.assertEqual(events_list.events[0], self.event1)
        self.assertEqual(events_list.events[1], self.event2)

    def test_initial_events_list_tip(self):
        events_list = Events([self.event1, self.event2])
        self.assertEqual(len(events_list.events), 2)
        self.assertEqual(events_list.events[0].tip, False)
        self.assertEqual(events_list.events[1].tip, True)

    def test_append_event(self):
        events_list = Events(self.event1)
        events_list.append(self.event2)
        self.assertEqual(len(events_list.events), 2)
        self.assertEqual(events_list.events[0], self.event1)
        self.assertEqual(events_list.events[1], self.event2)

    def test_append_events(self):
        events_list = Events(self.event1)
        events_list.append([self.event2, self.event3])
        self.assertEqual(len(events_list.events), 3)
        self.assertEqual(events_list.events[0], self.event1)
        self.assertEqual(events_list.events[1], self.event2)
        self.assertEqual(events_list.events[2], self.event3)

    def test_append_event_tip(self):
        events_list = Events(self.event1)
        events_list.append(self.event2)
        self.assertEqual(events_list.events[0].tip, False)
        self.assertEqual(events_list.events[1].tip, True)

    def test_get_event(self):
        events_list = Events([self.event1, self.event2])
        self.assertEqual(events_list.get_event(1), self.event1)
        self.assertEqual(events_list.get_event(2), self.event2)

    def test_filter_events(self):
        events_list = Events([self.event1, self.event2, self.event3])
        filtered_events_list = events_list.filter_by_duration()
        self.assertEqual(len(filtered_events_list), 2)


if __name__ == '__main__':
    unittest.main()
