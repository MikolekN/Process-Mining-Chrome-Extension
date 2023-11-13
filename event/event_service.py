import os
from datetime import datetime, timedelta
import json
import pandas as pd
import pm4py

from case.cases import Cases, Case
from event.event_repository import EventRepository
from event.events import Events, Event
from method_return import Success, Failure


def validate_data(data):
    expected_keys = ['eventId',
                     'timestamp',
                     'fromVisit',
                     'title',
                     'url',
                     'transition',
                     'duration',
                     'tip']
    validated_data = {}
    for key in expected_keys:
        if key not in data.keys():
            return Failure(f"Provided data is missing a value for {key} key.")
        validated_data[key] = data[key]
    return Success(validated_data)


def validate_date_data(data):
    expected_keys = ['startDate',
                     'endDate']
    validated_date_data = {}
    for key in expected_keys:
        if key in data:
            validated_date_data[key] = data[key]
        else:
            validated_date_data[key] = None
    return Success(validated_date_data)


def model_eventlog(xes_path):
    xes = pm4py.read_xes(xes_path)
    print("Loaded xes")
    dfg, start_activities, end_activities = pm4py.discovery.discover_dfg(xes, activity_key='title',
                                                                         timestamp_key='timestamp',
                                                                         case_id_key='case_id')
    print("Created dfg")
    image_path = os.path.join(os.path.expanduser('~'), "image.png")
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, image_path)
    print("Created image")
    return Success(image_path)


class EventService:

    def __init__(self, testing=False):
        self.repository = EventRepository(testing)

        self.start_date = None
        self.end_date = None
        self.is_model_up_to_date = False
        # value at which the events will be filtered out (in milliseconds)
        self.filter_value = 0

        self.cases = Cases()
        self.events = Events(update_cases=self.cases.update_cases)

    # Returns events as a raw json data.
    def get_events(self, data):
        validate = validate_date_data(data)
        if not validate.ok:
            return validate
        validated_date_data = validate.data

        self.set_date(validated_date_data)

        response = self.repository.get_events()
        if not response.ok:
            return response

        self.set_filter(response.data)

        response = self.filter_json_events(response.data)

        return response

    def filter_json_events(self, json_data):
        filtered_json = []
        for e in json_data:
            if e['duration'] > self.filter_value:
                filtered_json.append(e)
        return Success(filtered_json)

    # # A helper function that gathers events into the events list and creates the cases list
    # def load_events(self):
    #     response = self.repository.get_events()
    #
    #     if response.ok:
    #         events = [Event.deserialize(e) for e in response.data]
    #         self.cases = Cases()
    #         self.events = Events(initial_events=events, update_cases=self.cases.update_cases)
    #
    #         self.filter_events()
    #
    #     return response

    def filter_events(self):
        filtered_cases = []
        for case in self.cases.cases:
            filtered_case = []
            for event in case.events:
                if event.duration > self.filter_value:
                    filtered_case.append(event)
            if len(filtered_case) > 0:
                filtered_cases.append(Case(filtered_case))
        self.cases.cases = filtered_cases
        return Success(filtered_cases)

    def set_date(self, date_data):
        self.start_date = date_data['startDate']
        self.end_date = date_data['endDate']
        return Success("Setting date successful")

    def set_filter(self, events):
        new_start_date = self.start_date
        if new_start_date is None:
            new_start_date = datetime.fromtimestamp(events[0]['timestamp'] / 1000000)
        else:
            new_start_date = datetime.strptime(new_start_date, "%Y-%m-%d")

        new_end_date = self.end_date
        if new_end_date is None:
            new_end_date = datetime.fromtimestamp(events[-1]['timestamp'] / 1000000)
        else:
            new_end_date = datetime.strptime(new_end_date, "%Y-%m-%d")

        time_difference = new_end_date - new_start_date
        if time_difference.days < 1:
            self.filter_value = 0
        else:
            self.filter_value = 60000

        return Success("Setting filter successful")

    def post_events(self, data):
        validate = validate_data(data)
        if not validate.ok:
            return validate
        validated_data = validate.data

        post = self.repository.post_events(validated_data)

        # if post.ok and (self.end_date is None or datetime.fromtimestamp(post.data['timestamp']) <= self.end_date):
        #     self.is_model_up_to_date = False

        return post

    def get_event_by_id(self, _id):
        if len(self.events.events) != 0:
            for event in self.events.events:
                if event._id == _id:
                    return Success(json.loads(json.dumps(event, default=vars)))

        response = self.repository.get_event_by_id(_id)
        return response

    def get_event_by_event_id(self, eventId):
        if len(self.events.events) != 0:
            for event in self.events.events:
                if event.eventId == eventId:
                    return Success(json.loads(json.dumps(event, default=vars)))
        response = self.repository.get_event_by_event_id(eventId)
        return response

    def get_database(self):
        response = self.repository.get_database()
        return response

    def read_data_to_export(self):
        case_ids = []
        event_ids = []
        from_ids = []
        timestamps = []
        transitions = []
        durations = []
        titles = []
        urls = []

        for case_index, case in enumerate(self.cases.cases):
            for event in case.events:
                case_ids.append(str(case_index))
                event_ids.append(event.eventId)
                from_ids.append(event.fromVisit)
                timestamps.append(datetime(1601, 1, 1) + timedelta(microseconds=event.timestamp))
                transitions.append(event.transition)
                durations.append(event.duration)
                titles.append(event.title)
                urls.append(event.url)

        data = {
            "case_id": case_ids,
            "event_id": event_ids,
            "from_id": from_ids,
            "timestamp": timestamps,
            "transition": transitions,
            "duration": durations,
            "title": titles,
            "url": urls,
        }

        df = pd.DataFrame(data)

        return df

    def export_to_xes(self):
        df = self.read_data_to_export()
        xes_path = os.path.join(os.path.expanduser('~'), "XES.xes")
        pm4py.write_xes(df, xes_path, "case_id")
        return Success(xes_path)

    def eventlog_to_json(self):
        eventlog = {}
        for case_index, case in enumerate(self.cases.cases):
            events = []
            for event in case.events:
                e = event.serialize()
                events.append(e)
            eventlog[str(case_index)] = events
        return Success(eventlog)

    def get_eventlog(self, data):
        validate = validate_date_data(data)
        if not validate.ok:
            return validate
        validated_date_data = validate.data

        self.set_date(validated_date_data)

        response = self.repository.get_events()
        if not response.ok:
            return response

        self.set_filter(response.data)

        events = [Event.deserialize(e) for e in response.data]
        self.cases = Cases()
        self.events = Events(initial_events=events, update_cases=self.cases.update_cases)

        response = self.filter_events()
        if not response.ok:
            return response

        response = self.eventlog_to_json()

        return response

    def get_xes(self, data):
        validate = validate_date_data(data)
        if not validate.ok:
            return validate
        validated_date_data = validate.data

        self.set_date(validated_date_data)

        response = self.repository.get_events()
        if not response.ok:
            return response

        self.set_filter(response.data)

        events = [Event.deserialize(e) for e in response.data]
        self.cases = Cases()
        self.events = Events(initial_events=events, update_cases=self.cases.update_cases)

        response = self.filter_events()
        if not response.ok:
            return response

        response = self.export_to_xes()

        return response

    def get_image(self, data):
        validate = validate_date_data(data)
        if not validate.ok:
            return validate
        validated_date_data = validate.data
        print(validated_date_data)

        self.set_date(validated_date_data)
        print(self.start_date)
        print(self.end_date)

        response = self.repository.get_events()
        if not response.ok:
            return response

        self.set_filter(response.data)
        print(self.filter_value)

        events = [Event.deserialize(e) for e in response.data]
        self.cases = Cases()
        self.events = Events(initial_events=events, update_cases=self.cases.update_cases)
        print("Created cases")

        response = self.filter_events()
        if not response.ok:
            return response
        print("Filtered events")
        print(len(self.events.events))

        response = self.export_to_xes()
        if not response.ok:
            return response

        xes_path = response.data
        print(xes_path)

        response = model_eventlog(xes_path)
        if not response.ok:
            return response
        print(response.data)

        return response
