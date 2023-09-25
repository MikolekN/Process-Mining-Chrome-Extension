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
            result = self.service.get_events()
            if result.ok:
                return make_response(jsonify(result.data), 200)
            else:
                return make_response(jsonify(result.message), 500)

        @event_blueprint.route('', methods=['POST'])
        def post_events():
            data = request.get_json()
            result = self.service.post_events(data)
            if result.ok:
                return make_response(jsonify(result.data), 200)
            return make_response(jsonify(result.message), 500)

        @event_blueprint.route('/event/<string:_id>', methods=['GET'])
        def get_event_by_id(_id):
            result = self.service.get_event_by_id(_id)
            if result.ok:
                return make_response(jsonify(result.data), 200)
            return make_response(jsonify(result.message), 404)

        @event_blueprint.route('/eventId/<int:eventId>', methods=['GET'])
        def get_event_by_event_id(eventId):
            result = self.service.get_event_by_event_id(eventId)
            if result.ok:
                return make_response(jsonify(result.data), 200)
            return make_response(jsonify(result.message), 404)

        return event_blueprint
