import json
import os

import bson

import config
from method_return import Success, Failure


class EventRepository:
    def __init__(self, testing=False):
        db_name = config.TestConfig.DB_NAME if testing else config.Config.DB_NAME
        home_directory = os.path.expanduser('~')
        self.db = os.path.join(home_directory, db_name + ".json")
        self.create_file_if_not_exists()

    def get_events(self):
        try:
            with open(self.db, 'r') as file:
                events = json.load(file)
                if not isinstance(events, list):
                    events = [events]
        except FileNotFoundError:
            events = []
        return Success(events)

    def create_file_if_not_exists(self):
        try:
            with open(self.db, 'r'):
                pass
        except FileNotFoundError:
            with open(self.db, 'w') as file:
                json.dump([], file)

    def post_events(self, data):
        self.create_file_if_not_exists()
        with open(self.db, 'r') as file:
            events = json.load(file)
            if not isinstance(events, list):
                events = [events]

        for event in events:
            if event['eventId'] == data['eventId']:
                return Failure("An event with given eventId already exists.")

        data['_id'] = str(bson.ObjectId())
        events.append(data)

        with open(self.db, 'w') as file:
            json.dump(events, file)

        return Success(data)

    def get_event_by_id(self, _id):
        try:
            with open(self.db, 'r') as file:
                events = json.load(file)
                if not isinstance(events, list):
                    events = [events]
        except FileNotFoundError:
            events = []
        for event in events:
            if event['_id'] == _id:
                return Success(event)
        return Failure("No event with given _id was found.")

    def get_event_by_event_id(self, eventId):
        try:
            with open(self.db, 'r') as file:
                events = json.load(file)
                if not isinstance(events, list):
                    events = [events]
        except FileNotFoundError:
            events = []
        for event in events:
            if event['eventId'] == eventId:
                return Success(event)
        return Failure("No event with given eventId was found.")

    def get_database(self):
        return Success(self.db)
