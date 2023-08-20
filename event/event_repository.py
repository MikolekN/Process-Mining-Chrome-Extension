from pymongo import MongoClient

from event.events import Event


# TODO handle no response (no returned item)
class EventRepository:
    def __init__(self):
        # Connect to the MongoDB server
        client = MongoClient('localhost', 27017)

        # Access the database and collection
        db = client['chrome_test_v3']
        self.events_collection = db['events']

    def get_events(self):
        events = self.events_collection.find()
        return events

    def get_event_by_id(self, _id):
        event = self.events_collection.find_one({'_id': _id})
        return event

    def get_event_by_event_id(self, eventId):
        event = self.events_collection.find_one({'eventId': eventId})
        return event
