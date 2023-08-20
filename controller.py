import flask
import flask_cors

from case import case_controller
from event import event_controller

app = flask.Flask(__name__)
flask_cors.CORS(app)

app.register_blueprint(event_controller.event_blueprint, url_prefix='/events')
app.register_blueprint(case_controller.case_blueprint, url_prefix='/cases')


def run():
    app.run(host='localhost', port=1234)


if __name__ == '__main__':
    app.run(host='localhost', port=1234)
