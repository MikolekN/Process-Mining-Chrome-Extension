import unittest
from case.cases import Case, Cases
from event.events import Event


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.event1 = Event(eventId=1, timestamp=1067232138, fromVisit=0, title="Visit 1", url="https://example.com",
                           transition="link", duration=10)
        cls.event2 = Event(eventId=2, timestamp=1699699158, fromVisit=1, title="Visit 2",
                           url="https://example.com/page",
                           transition="link", duration=5)

    def test_case_creation_empty(self):
        case = Case()
        self.assertEqual(len(case.events), 0)

    def test_case_creation_single(self):
        case = Case(self.event1)
        self.assertEqual(len(case.events), 1)

    def test_case_creation_list(self):
        case = Case([self.event1, self.event2])
        self.assertEqual(len(case.events), 2)


class TestCases(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.event1 = Event(1, 1364207461, 0, "Visit 1", "https://example.com", "link", 10)
        cls.event2 = Event(2, 1020186737, 1, "Visit 2", "https://example.com/page", "link", 5)
        cls.event3 = Event(3, 1221717683, 2, "Visit 3", "https://example.com/page/page", "link", 0)

        cls.case1 = Case([cls.event1, cls.event2])
        cls.case2 = Case([cls.event2, cls.event3])

    def test_cases_creation_empty(self):
        cases = Cases()
        self.assertEqual(len(cases.cases), 0)

    def test_cases_creation_single(self):
        cases = Cases(self.case1)
        self.assertEqual(len(cases.cases), 1)

    def test_cases_creation_list(self):
        cases = Cases([self.case1, self.case2])
        self.assertEqual(len(cases.cases), 2)

    def test_cases_append_single(self):
        cases = Cases()
        cases.append(self.case1)
        self.assertEqual(len(cases.cases), 1)
        self.assertEqual(cases.cases[0], self.case1)

    def test_cases_append_list(self):
        cases = Cases()
        cases.append([self.case1, self.case2])
        self.assertEqual(len(cases.cases), 2)
        self.assertEqual(cases.cases[0], self.case1)
        self.assertEqual(cases.cases[1], self.case2)

    def test_cases_remove(self):
        cases = Cases(self.case1)
        cases.remove(self.case1)
        self.assertEqual(len(cases.cases), 0)

    def test_update_cases(self):
        cases = Cases([self.case1, self.case2])
        cases.update_cases(self.event3)
        self.assertEqual(len(cases.cases[0].events), 3)
        self.assertEqual(cases.cases[0].events[-1], self.event3)
        self.assertEqual(len(cases.cases[1].events), 2)
        self.assertEqual(cases.cases[1].events[-1], self.event3)
