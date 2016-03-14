import os
import json
from datetime import datetime

import flask
from flask import Flask, jsonify, abort, request
#from flask.ext.heroku import Heroku
from flask_heroku import Heroku
#from flask.ext.script import Manager
from flask_script import Manager
#from flask.ext.script import Server
from flask_script import Server
from memoize import Memoizer

from service.exchange import ExchangeCalendar


##################################################
#                    Setup
##################################################

app = Flask(__name__)
app.debug = True
heroku = Heroku(app)

_allowed_ips = os.environ.get('OUTLOOK_ALLOWED_IPS', '')

store = {}
memo = Memoizer(store)

config = {
    'domain': os.environ['OUTLOOK_DOMAIN'],
    'ews_url': os.environ['OUTLOOK_EWS_URL'],  # EWS = Exchange Web Services
    'username': os.environ['OUTLOOK_USERNAME'],
    'password': os.environ['OUTLOOK_PASSWORD'],
    'allowed_ips': [ip.strip() for ip in _allowed_ips.split(',')] if _allowed_ips else [],
    'room_dict': os.environ.get('OUTLOOK_ROOM_DICT', ''),
    'room_search_term': os.environ.get('OUTLOOK_ROOM_SEARCH_TERM'),
    'poll_interval': os.environ.get('OUTLOOK_POLL_INTERVAL', 1),
    'poll_start_minute': os.environ.get('OUTLOOK_POLL_START_MINUTE', 420),
    'poll_end_minute': os.environ.get('OUTLOOK_POLL_END_MINUTE', 1140),
    'cache_time': os.environ.get('CACHE_TIME', 30),
}

exchange = ExchangeCalendar(config['domain'], config['ews_url'], config['username'], config['password'])

if config['room_dict']:
    MEETING_ROOMS = json.loads(config['room_dict'])
else:
    MEETING_ROOMS = {room['displayName']: room['email'] for room in exchange.get_contacts(config['room_search_term'])}


def _transform_booking_info(booking):
    start = booking.pop('start')
    end = booking.pop('end')
    booking.pop('description')

    booking['start_minute'] = start.hour * 60 + start.minute
    booking['end_minute'] = end.hour * 60 + end.minute

    return booking


@app.before_request
def restrict_access():
    if config['allowed_ips'] and request.remote_addr not in config['allowed_ips']:
        abort(403)


@app.route('/')
def hello_world():
    return flask.send_file('./templates/index.html')


@app.route('/data')
def data():
    start = datetime.today().replace(hour=7, minute=0, second=0, microsecond=0)
    end = datetime.today().replace(hour=23, minute=0, second=0, microsecond=0)
    id_namespace = ".".join(reversed(config['ews_url'].split('//', 1)[1].split('/')[0].split('.')))

    ret = {
        "polling": {
            "interval": config['poll_interval'],
            "start_minute": config['poll_start_minute'],
            "end_minute": config['poll_end_minute'],
        },
        "rooms": [],
    }

    return get_meeting_room_data(start, end, id_namespace, ret)

@memo(max_age=config['cache_time'])
def get_meeting_room_data(start, end, id_namespace, ret):
    for room_name, room_email in MEETING_ROOMS.iteritems():
        meeting_room_details = {
            "id": "{}.{}".format(id_namespace, room_email.split('@')[0]),
            "name": room_name,
            "description": None,
            "bookings": [_transform_booking_info(booking) for booking in exchange.get_bookings(start, end, room_email)]
        }
        ret["rooms"].append(meeting_room_details)

    return jsonify(ret)


##################################################
#                    Main
##################################################

manager = Manager(app)
# Bind the dev server to 0.0.0.0 so it works through Docker
manager.add_command('runserver', Server(host='0.0.0.0'))

@manager.command
def production():
    """
    Run the server in production mode
    """
    # Turn off debug on live...
    app.debug = False

    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    print('Running on port {PORT}'.format(PORT=port))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    manager.run()
