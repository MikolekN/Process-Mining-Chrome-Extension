from flask import Blueprint, make_response, jsonify, request, send_file

from event.event_service import EventService


class EventController:
    def __init__(self, testing=False):
        self.service = EventService(testing)
        self.event_blueprint = self.construct_event_blueprint()

    def construct_event_blueprint(self):
        event_blueprint = Blueprint('event_blueprint', __name__)

        # Returns raw json data filtered by provided startDate and endDate
        @event_blueprint.route('', methods=['GET'])
        def get_events():
            data = request.get_json()
            result = self.service.get_events(data)
            if result.ok:
                return make_response(jsonify(result.data), 200)
            return make_response(jsonify(result.message), 500)

        @event_blueprint.route('', methods=['POST'])
        def post_events():
            data = request.get_json()
            result = self.service.post_events(data)
            if result.ok:
                return make_response(jsonify(result.data), 200)
            return make_response(jsonify(result.message), 500)

        # @event_blueprint.route('/event/<string:_id>', methods=['GET'])
        # def get_event_by_id(_id):
        #     result = self.service.get_event_by_id(_id)
        #     if result.ok:
        #         return make_response(jsonify(result.data), 200)
        #     return make_response(jsonify(result.message), 404)
        #
        # @event_blueprint.route('/eventId/<int:eventId>', methods=['GET'])
        # def get_event_by_event_id(eventId):
        #     result = self.service.get_event_by_event_id(eventId)
        #     if result.ok:
        #         return make_response(jsonify(result.data), 200)
        #     return make_response(jsonify(result.message), 404)

        @event_blueprint.route('/database', methods=['GET'])
        def get_database():
            result = self.service.get_database()
            if result.ok:
                database_path = result.data
                return send_file(path_or_file=database_path,
                                 mimetype="application/json",
                                 as_attachment=True,
                                 download_name='database.json',
                                 conditional=True,
                                 etag=True,
                                 last_modified=None,
                                 max_age=None)
            return make_response(jsonify(result.message), 404)

        @event_blueprint.route('/eventlog', methods=['GET'])
        def get_eventlog():
            data = request.get_json()
            result = self.service.get_eventlog(data)
            if result.ok:
                return make_response(jsonify(result.data), 200)
            return make_response(jsonify(result.message), 404)

        @event_blueprint.route('/xes', methods=['GET'])
        def get_xes():
            data = request.get_json()
            result = self.service.get_xes(data)
            if result.ok:
                xes_path = result.data
                return send_file(path_or_file=xes_path,
                                 mimetype="application/xml",
                                 as_attachment=True,
                                 download_name='xes.xes',
                                 conditional=True,
                                 etag=True,
                                 last_modified=None,
                                 max_age=None)
            return make_response(jsonify(result.message), 500)

        @event_blueprint.route('/image', methods=['GET'])
        def get_image():
            if request.is_json:
                data = request.get_json()
            else:
                data = {}
            result = self.service.get_image(data)
            if result.ok:
                image_path = result.data
                return send_file(path_or_file=image_path,
                                 mimetype="image/png",
                                 as_attachment=True,
                                 download_name='image.png',
                                 conditional=True,
                                 etag=True,
                                 last_modified=None,
                                 max_age=None)
            return make_response(jsonify(result.message), 500)

        return event_blueprint
