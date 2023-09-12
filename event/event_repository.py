from pymongo import MongoClient
import sys

import config


# TODO handle no response (no returned item)
class EventRepository:
    def __init__(self):
        testing_mode = '--testing' in sys.argv
        db_name = config.TestConfig.DB_NAME if testing_mode else config.Config.DB_NAME
        client = MongoClient('localhost', 27017)
        db = client[db_name]
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
