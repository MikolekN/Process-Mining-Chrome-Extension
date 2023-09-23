from event.event_repository import EventRepository
from method_return import Success, Failure


class EventService:
    def __init__(self, testing=False):
        self.repository = EventRepository(testing)

    def get_events(self):
        events = self.repository.get_events()
        return events

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
        return post

    def get_event_by_id(self, _id):
        event = self.repository.get_event_by_id(_id)
        return event if event else None

    def get_event_by_event_id(self, eventId):
        event = self.repository.get_event_by_event_id(eventId)
        return event if event else None
