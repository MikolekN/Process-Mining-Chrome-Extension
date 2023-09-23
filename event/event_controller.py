from flask import Blueprint, make_response, jsonify, request

from event.event_service import EventService


class EventController:
    def __init__(self, testing=False):
        self.service = EventService(testing)
        self.event_blueprint = self.construct_event_blueprint()

    def construct_event_blueprint(self):
        event_blueprint = Blueprint('event_blueprint', __name__)

        @event_blueprint.route('', methods=['GET'])
        def get_events():
            events = self.service.get_events()
            return events

        @event_blueprint.route('', methods=['POST'])
        def post_events():
            data = request.get_json()
            result = self.service.post_events(data)
            if not result.ok:
                return result.message
            return result.data

        @event_blueprint.route('/event/<string:_id>', methods=['GET'])
        def get_event_by_id(_id):
            event = self.service.get_event_by_id(_id)
            if event is None:
                return make_response(jsonify({'message': 'Event not found'}), 404)
            return event

        @event_blueprint.route('/eventId/<int:eventId>', methods=['GET'])
        def get_event_by_event_id(eventId):
            event = self.service.get_event_by_event_id(eventId)
            if event is None:
                return make_response(jsonify({'message': 'Event not found'}), 404)
            return event

        return event_blueprint
