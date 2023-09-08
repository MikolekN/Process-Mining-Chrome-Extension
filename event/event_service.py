from bson import ObjectId

from event.event_repository import EventRepository


class EventService:
    def __init__(self):
        self.repository = EventRepository()

    def get_events(self):
        events = self.repository.get_events()
        return [{
            'eventId': event['eventId'],
            'timestamp': event['timestamp'],
            'fromVisit': event['fromVisit'],
            'title': event['title'],
            'url': event['url'],
            'transition': event['transition'],
            'duration': event['duration'],
            'tip': event['tip'],
            '_ownerId': str(event['_ownerId']),
            '_id': str(event['_id'])
        } for event in events]

    def get_event_by_id(self, _id):
        event = self.repository.get_event_by_id(ObjectId(_id))
        return {
            'eventId': event['eventId'],
            'timestamp': event['timestamp'],
            'fromVisit': event['fromVisit'],
            'title': event['title'],
            'url': event['url'],
            'transition': event['transition'],
            'duration': event['duration'],
            'tip': event['tip'],
            '_ownerId': str(event['_ownerId']),
            '_id': str(event['_id'])
        } if event else None

    def get_event_by_event_id(self, eventId):
        event = self.repository.get_event_by_event_id(eventId)
        return {
            'eventId': event['eventId'],
            'timestamp': event['timestamp'],
            'fromVisit': event['fromVisit'],
            'title': event['title'],
            'url': event['url'],
            'transition': event['transition'],
            'duration': event['duration'],
            'tip': event['tip'],
            '_ownerId': str(event['_ownerId']),
            '_id': str(event['_id'])
        } if event else None
