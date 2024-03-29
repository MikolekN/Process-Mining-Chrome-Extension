import os
from datetime import datetime, timedelta
import pandas as pd
import pm4py

from event.event_repository import EventRepository
from method_return import Success, Failure


def validate_data(data):
    """
        Validates the given event data based on expected keys.
        There are keys that need to be present for an event to be valid.

        Args:
        - data (dict): The event data to be validated.

        Returns:
        - Success: If the data is valid.
        - Failure: If the data is missing any expected key.
    """
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
    """
        Validates the given date data based on expected keys.
        startDate and endDate keys need to be present for date to be valid.

        Args:
        - data (dict): The date data to be validated.

        Returns:
        - Success: If the data is valid.
        - Failure: If the data is missing any expected keys.
    """
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
    """
        Models an event log into an image from a given XES file.

        Args:
        - xes_path (str): The path to the XES file.

        Returns:
        - Success: If modeling is successful, providing the path to the generated image.
        - Failure: If an error occurs during modeling.
    """
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
        """
            Gets the path to the database.

            Returns:
            - Success: If the database path is obtained successfully.
            - Failure: If an error occurs during the process.
        """
        response = self.repository.get_database()
        return response

    def get_events(self, data):
        """
            Gets filtered events based on provided data.

            Args:
            - data (dict): Data specifying the time range for events.

            Returns:
            - Success: If events are retrieved successfully.
            - Failure: If an error occurs during the process.
        """
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
        """
            Filters list of JSON events based on duration.

            Args:
            - json_data (list): List of JSON events.

            Returns:
            - Success: If filtering is successful, providing the filtered JSON events.
            - Failure: If an error occurs during filtering.
        """
        filtered_json = []
        for event in json_data:
            if self.start_date is None or datetime.strptime(self.start_date, "%Y-%m-%d") <= datetime(1970, 1, 1) + timedelta(milliseconds=int(event['timestamp'])):
                if self.end_date is None or datetime(1970, 1, 1) + timedelta(milliseconds=int(event['timestamp'])) <= datetime.strptime(self.end_date, "%Y-%m-%d"):
                    if event['duration'] > self.filter_value:
                        filtered_json.append(event)
        return Success(filtered_json)

    def set_filter(self, events):
        """
            Sets the filter value based on the selected date range.

            Args:
            - events (list): List of events.

            Returns:
            - Success: If setting the filter is successful.
        """
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
                smooth_transition_factor = min(1.0, len(events) / 1500.0, time_difference.days / 30.0)
                target_filter_value = int(smooth_transition_factor * 60000)
                if self.filter_value != target_filter_value:
                    self.filter_value = target_filter_value
                    self.is_model_up_to_date = False
                    self.is_cases_up_to_date = False

        return Success("Setting filter successful")

    def set_date(self, date_data):
        """
            Sets the start and end dates based on provided date data.

            Args:
            - date_data (dict): Date data specifying start and end dates.

            Returns:
            - Success: If setting the date is successful.
        """
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
        """
            Posts events to the event database.

            Args:
            - data (dict): Event data to be posted.

            Returns:
            - Success: If posting is successful.
            - Failure: If an error occurs during posting.
        """
        validate = validate_data(data)
        if not validate.ok:
            return validate
        validated_data = validate.data

        post = self.repository.post_events(validated_data)

        # If the events is in range of selected date the model will need to be updated
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

    # Gets an event by its ID.
    def get_event_by_id(self, _id):
        return self.repository.get_event_by_id(_id)

    # Gets an event by its eventId.
    def get_event_by_event_id(self, eventId):
        return self.repository.get_event_by_event_id(eventId)

    def get_eventlog(self, data):
        """
            Gets an event log based on provided data.

            Args:
            - data (dict): Data specifying the time range for events.

            Returns:
            - Success: If obtaining the event log is successful.
            - Failure: If an error occurs during the process.
        """
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
            response = self.filter_cases()
            if not response.ok:
                return response
            self.is_cases_up_to_date = True

        return Success(self.cases)

    def filter_cases(self):
        self.cases = [[event for event in chain if event['duration'] > self.filter_value] for chain in self.cases]
        self.cases = [chain for chain in self.cases if len(chain) != 0]

        self.cases = \
            [
                [
                    event for event in case
                    if (self.start_date is None or datetime.strptime(self.start_date, "%Y-%m-%d") <= datetime(1970, 1, 1) + timedelta(milliseconds=int(event['timestamp'])))
                       and (self.end_date is None or datetime(1970, 1, 1) + timedelta(milliseconds=int(event['timestamp'])) <= datetime.strptime(self.end_date, "%Y-%m-%d"))
                ] for case in self.cases
            ]
        self.cases = [chain for chain in self.cases if len(chain) != 0]
        
        return Success(self.cases)

    def chain_events(self, events):
        """
            Chains events based on the 'fromVisit' attribute creating cases.

            Args:
            - events (list): List of events.

            Returns:
            - Success: If chaining events is successful, providing the chained events.
            - Failure: If an error occurs during chaining.
        """
        event_map = {event['eventId']: event for event in events}
        self.cases = []

        for event in events:
            if event['fromVisit'] == 0 or event['fromVisit'] == '0':
                self.cases.append([event])

        for event in events:
            if event['fromVisit'] != 0 and event['fromVisit'] != '0':
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
                else:
                    self.cases.append([event])

        return Success(self.cases)

    def get_xes(self, data):
        """
            Gets XES data based on provided data.

            Args:
            - data (dict): Data specifying the time range for events.

            Returns:
            - Success: If obtaining XES data is successful.
            - Failure: If an error occurs during the process.
        """
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
            response = self.filter_cases()
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
        """
            Exports event log data to XES format.

            Returns:
            - Success: If exporting to XES is successful, providing the path to the XES file.
            - Failure: If an error occurs during exporting.
        """
        df = self.read_data_to_export()
        xes_path = os.path.join(os.path.expanduser('~'), "XES.xes")
        try:
            pm4py.write_xes(df, xes_path, activity_key='title', timestamp_key='timestamp', case_id_key='case_id')
        except Exception as e:
            return Failure(str(e))
        return Success(xes_path)

    def read_data_to_export(self):
        """
            Prepares data for export to XES format.

            Returns:
            - DataFrame: Pandas DataFrame containing data for export.
        """
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
        """
            Gets an image based on provided data.

            Args:
            - data (dict): Data specifying the time range for events.

            Returns:
            - Success: If obtaining the image is successful.
            - Failure: If an error occurs during the process.
        """
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
            response = self.filter_cases()
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
