import os
import sqlite3

import pymongo

from case.cases import Cases
from event.events import Events, Event


def load_events(path_to_db):
    with sqlite3.connect(path_to_db) as conn:
        cursor = conn.cursor()
        select_statement = "SELECT visits.id, urls.title, urls.url, visits.visit_time, visits.from_visit, " \
                           "visits.transition, visits.visit_duration FROM urls, visits WHERE urls.id = visits.url;"
        cursor.execute(select_statement)
        results = cursor.fetchall()
        events = []
        for eventId, title, url, timestamp, fromVisit, transition, duration in results:
            events.append(Event(eventId=eventId, timestamp=timestamp, fromVisit=fromVisit, title=title, url=url,
                                transition=transition, duration=duration))
        return events


def main():
    # Get the data
    cases = Cases()
    events = Events(update_cases=cases.update_cases, initial_events=load_events(os.path.expanduser('~') + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\history"))
    user = {"email": 'mail@mail.com', "passwordHash": 'HASHhalloHASH'}

    # Connect to mongodb
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["chrome_test_v3"]
    users_collection = database["users"]
    events_collection = database["events"]
    cases_collection = database["cases"]

    # Insert the data
    user_id = users_collection.insert_one(user).inserted_id

    events_data = []
    for event in events.events:
        events_data.append(
            {"eventId": event.eventId, "timestamp": event.timestamp, "fromVisit": event.fromVisit,
             "title": event.title, "url": event.url, "transition": event.transition, "duration": event.duration,
             "tip": event.tip})

    event_ids = []
    for event in events_data:
        event_ids.append(events_collection.insert_one(event).inserted_id)

    def findId(event):
        for i, e in enumerate(events_data):
            if e["eventId"] == event.eventId:
                return event_ids[i]

    cases_data = []
    for case in cases.cases:
        cases_data.append({"caseEvents": [findId(event) for event in case.events]})

    case_ids = []
    for case in cases_data:
        case_ids.append(cases_collection.insert_one(case).inserted_id)


if __name__ == '__main__':
    main()
