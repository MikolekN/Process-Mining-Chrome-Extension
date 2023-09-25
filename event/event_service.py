import json

from case.cases import Cases
from event.event_repository import EventRepository
from event.events import Events, Event
from method_return import Success, Failure


class EventService:
    def __init__(self, testing=False):
        self.repository = EventRepository(testing)

        self.cases = Cases()
        self.events = Events(update_cases=self.cases.update_cases)

    def get_events(self):
        if len(self.events.events) != 0:
            return Success(json.loads(json.dumps(self.events.events, default=vars)))

        response = self.repository.get_events()

        if response.ok:
            events = [Event.deserialize(e) for e in response.data]
            self.cases = Cases()
            self.events = Events(initial_events=events, update_cases=self.cases.update_cases)

        return response

    def validate_data(self, data):
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

    def post_events(self, data):
        validate = self.validate_data(data)
        if not validate.ok:
            return validate
        validated_data = validate.data

        post = self.repository.post_events(validated_data)

        if post.ok:
            self.events.append(Event.deserialize(post.data))

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
