from event.event_service import EventService

from flask import Blueprint

event_blueprint = Blueprint('event_blueprint', __name__)
event_service = EventService()


@event_blueprint.route('', methods=['GET'])
def get_events():
    events = event_service.get_events()
    return events


@event_blueprint.route('/event/<string:_id>', methods=['GET'])
def get_event_by_id(_id):
    event = event_service.get_event_by_id(_id)
    return event


@event_blueprint.route('/eventId/<int:eventId>', methods=['GET'])
def get_event_by_event_id(eventId):
    event = event_service.get_event_by_event_id(eventId)
    return event
