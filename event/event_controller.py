from event.event_service import EventService

from flask import Blueprint, make_response, jsonify, request

event_blueprint = Blueprint('event_blueprint', __name__)
event_service = EventService()


@event_blueprint.route('', methods=['GET'])
def get_events():
    events = event_service.get_events()
    return events


@event_blueprint.route('', methods=['POST'])
def post_events():
    data = request.get_json()
    result = event_service.post_events(data)
    if not result.ok:
        return result.message
    return event_service.get_event_by_id(result.data)


@event_blueprint.route('/event/<string:_id>', methods=['GET'])
def get_event_by_id(_id):
    event = event_service.get_event_by_id(_id)
    if event is None:
        return make_response(jsonify({'message': 'Event not found'}), 404)
    return event


@event_blueprint.route('/eventId/<int:eventId>', methods=['GET'])
def get_event_by_event_id(eventId):
    event = event_service.get_event_by_event_id(eventId)
    if event is None:
        return make_response(jsonify({'message': 'Event not found'}), 404)
    return event
