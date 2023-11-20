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
    dfg, start_activities, end_activities = pm4py.discovery.discover_dfg(xes, activity_key='title',
                                                                         timestamp_key='timestamp',
                                                                         case_id_key='case_id')
    image_path = os.path.join(os.path.expanduser('~'), "image.png")
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, image_path)
    return Success(image_path)


class EventService:

    def __init__(self, testing=False):
        self.repository = EventRepository(testing)

        self.start_date = None
        self.end_date = None

        self.is_model_up_to_date = False
        self.is_cases_up_to_date = False

        self.filter_value = 0

        self.cases = []

        self.xes_path = None

    def get_database(self):
        response = self.repository.get_database()
        return response

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

    def set_filter(self, events):
        if len(events) == 0:
            if self.filter_value != 0:
                self.filter_value = 0
                self.is_model_up_to_date = False
                self.is_cases_up_to_date = False
        else:
            if self.start_date is None:
                new_start_date = datetime(1970, 1, 1) + timedelta(milliseconds=int(events[0]['timestamp']))
            else:
                new_start_date = datetime.strptime(self.start_date, "%Y-%m-%d")

            if self.end_date is None:
                new_end_date = datetime(1970, 1, 1) + timedelta(milliseconds=int(events[-1]['timestamp']))
            else:
                new_end_date = datetime.strptime(self.end_date, "%Y-%m-%d")

            time_difference = new_end_date - new_start_date
            if time_difference.days < 1:
                if self.filter_value != 0:
                    self.filter_value = 0
                    self.is_model_up_to_date = False
                    self.is_cases_up_to_date = False
            else:
                if self.filter_value != 60000:
                    self.filter_value = 60000
                    self.is_model_up_to_date = False
                    self.is_cases_up_to_date = False

        return Success("Setting filter successful")

    def set_date(self, date_data):
        if date_data['startDate'] is not None:
            new_start_date = datetime.strptime(date_data['startDate'], "%Y-%m-%d")
            if self.start_date is None or new_start_date != datetime.strptime(self.start_date, "%Y-%m-%d"):
                self.start_date = date_data['startDate']
                self.is_model_up_to_date = False
                self.is_cases_up_to_date = False
        elif self.start_date is not None:
            self.start_date = None
            self.is_model_up_to_date = False
            self.is_cases_up_to_date = False

        if date_data['endDate'] is not None:
            new_end_date = datetime.strptime(date_data['endDate'], "%Y-%m-%d")
            if self.end_date is None or new_end_date != datetime.strptime(self.end_date, "%Y-%m-%d"):
                self.end_date = date_data['endDate']
                self.is_model_up_to_date = False
                self.is_cases_up_to_date = False
        elif self.end_date is not None:
            self.end_date = None
            self.is_model_up_to_date = False
            self.is_cases_up_to_date = False

        return Success("Setting date successful")

    def post_events(self, data):
        validate = validate_data(data)
        if not validate.ok:
            return validate
        validated_data = validate.data

        post = self.repository.post_events(validated_data)

        if post.ok:
            event_date = datetime(1970, 1, 1) + timedelta(milliseconds=int(post.data['timestamp']))
            if self.start_date is None and self.end_date is None:
                self.is_model_up_to_date = False
                self.is_cases_up_to_date = False
            elif self.start_date is not None and self.end_date is not None:
                start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
                end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
                if start_date < event_date < end_date:
                    self.is_model_up_to_date = False
                    self.is_cases_up_to_date = False
            elif self.start_date is not None:
                start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
                if start_date < event_date:
                    self.is_model_up_to_date = False
                    self.is_cases_up_to_date = False
            elif self.end_date is not None:
                end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
                if event_date < end_date:
                    self.is_model_up_to_date = False
                    self.is_cases_up_to_date = False

        return post

    # def get_event_by_id(self, _id):
    #     if len(self.events.events) != 0:
    #         for event in self.events.events:
    #             if event._id == _id:
    #                 return Success(json.loads(json.dumps(event, default=vars)))
    #
    #     response = self.repository.get_event_by_id(_id)
    #     return response
    #
    # def get_event_by_event_id(self, eventId):
    #     if len(self.events.events) != 0:
    #         for event in self.events.events:
    #             if event.eventId == eventId:
    #                 return Success(json.loads(json.dumps(event, default=vars)))
    #     response = self.repository.get_event_by_event_id(eventId)
    #     return response

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

        if not self.is_cases_up_to_date:
            response = self.chain_events(response.data)
            if response.ok:
                self.is_cases_up_to_date = True
            return response

        return Success(self.cases)

    def chain_events(self, events):
        event_map = {event['eventId']: event for event in events}
        self.cases = []

        for event in events:
            if event['fromVisit'] == 0 or event['fromVisit'] == '0':
                self.cases.append([event])

        for event in events:
            if event['fromVisit'] != 0:
                from_event = event_map.get(event['fromVisit'])
                if from_event:
                    added_to_chain = False
                    for chain in self.cases:
                        if len(chain) > 0:
                            if event['fromVisit'] == chain[-1]['eventId']:
                                added_to_chain = True
                                chain.append(event)
                                break
                            for index, e in enumerate(chain):
                                if e['eventId'] == event['fromVisit']:
                                    added_to_chain = True
                                    events = chain[:index + 1]
                                    events.append(event)
                                    self.cases.append(events)
                                    break
                            if added_to_chain:
                                break
                    if not added_to_chain:
                        self.cases.append([event])

        self.cases = [[event for event in chain if event['duration'] > self.filter_value] for chain in self.cases]

        return Success(self.cases)

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

        if not self.is_cases_up_to_date:
            response = self.chain_events(response.data)
            if not response.ok:
                return response
            self.is_cases_up_to_date = True

        if not self.is_model_up_to_date:
            if len(self.cases) == 0:
                return Failure("Database is empty")

            response = self.export_to_xes()
            if response.ok:
                self.xes_path = response.data
                self.is_model_up_to_date = True

            return response

        return Success(self.xes_path)

    def export_to_xes(self):
        df = self.read_data_to_export()
        xes_path = os.path.join(os.path.expanduser('~'), "XES.xes")
        try:
            pm4py.write_xes(df, xes_path, activity_key='title', timestamp_key='timestamp', case_id_key='case_id')
        except Exception as e:
            return Failure(str(e))
        return Success(xes_path)

    def read_data_to_export(self):
        case_ids = []
        event_ids = []
        from_ids = []
        timestamps = []
        transitions = []
        durations = []
        titles = []
        urls = []

        for case_index, case in enumerate(self.cases):
            for event in case:
                case_ids.append(str(case_index))
                event_ids.append(str(event['eventId']))
                from_ids.append(str(event['fromVisit']))
                timestamps.append(datetime(1970, 1, 1) + timedelta(milliseconds=int(event['timestamp'])))
                transitions.append(str(event['transition']))
                durations.append(str(event['duration']))
                titles.append(str(event['title']))
                urls.append(str(event['url']))

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

    def get_image(self, data):
        validate = validate_date_data(data)
        if not validate.ok:
            return validate
        validated_date_data = validate.data

        self.set_date(validated_date_data)

        response = self.repository.get_events()
        if not response.ok:
            return response

        self.set_filter(response.data)

        if not self.is_cases_up_to_date:
            response = self.chain_events(response.data)
            if not response.ok:
                return response
            self.is_cases_up_to_date = True

        if not self.is_model_up_to_date:
            if len(self.cases) == 0:
                return Failure("Database is empty")

            response = self.export_to_xes()
            if not response.ok:
                return response
            self.xes_path = response.data
            self.is_model_up_to_date = True

        response = model_eventlog(self.xes_path)
        return response
