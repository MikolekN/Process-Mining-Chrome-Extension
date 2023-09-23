import flask
import flask_cors

from event import event_controller

app = flask.Flask(__name__)
flask_cors.CORS(app)
controller = event_controller.EventController()
app.register_blueprint(controller.event_blueprint, url_prefix='/')


def run():
    app.run(host='localhost', port=1234)


if __name__ == '__main__':
    app.run(host='localhost', port=1234)
