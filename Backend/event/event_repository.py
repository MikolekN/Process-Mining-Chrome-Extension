import json
import os

import bson

import config
from method_return import Success, Failure

import msvcrt


class EventRepository:
    def __init__(self, testing=False):
        db_name = config.TestConfig.DB_NAME if testing else config.Config.DB_NAME
        home_directory = os.path.expanduser('~')
        self.db = os.path.join(home_directory, db_name + ".json")
        self.create_file_if_not_exists()

    # Function to get the path to the database
    def get_database(self):
        return Success(self.db)

    # Function to get events from the database
    def get_events(self):
        try:
            with open(self.db, 'r') as file:
                events = json.load(file)
                if not isinstance(events, list):
                    events = [events]
        except FileNotFoundError:
            events = []
        return Success(events)

    # Helper function to create the database file if it doesn't exist
    def create_file_if_not_exists(self):
        try:
            with open(self.db, 'r'):
                pass
        except FileNotFoundError:
            with open(self.db, 'w') as file:
                json.dump([], file)

    # Function to save events to the database
    def post_events(self, data):
        self.create_file_if_not_exists()

        lock_file = self.db + ".lock"
        with open(lock_file, "wb") as lock_fp:
            msvcrt.locking(lock_fp.fileno(), msvcrt.LK_LOCK, 1)
            try:
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
            finally:
                msvcrt.locking(lock_fp.fileno(), msvcrt.LK_UNLCK, 1)

        return Success(data)

    # Function to get an event by its ID from the database
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

    # Function to get an event by its eventId from the database
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
