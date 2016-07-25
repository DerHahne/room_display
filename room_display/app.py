import json
import os
import sys
from datetime import datetime

import flask
from flask import Flask, jsonify, abort, request
from flask_heroku import Heroku
from flask_script import Manager
from flask_script import Server


##################################################
#                    Setup
##################################################

app = Flask(__name__)
app.debug = True
heroku = Heroku(app)

_instabook_times = os.environ.get('INSTABOOK_TIMES', None)
_allowed_ips = os.environ.get('OUTLOOK_ALLOWED_IPS', None)

config = {
    # Misc settings
    'host': os.environ.get('HOST', '0.0.0.0'),
    'port': int(os.environ.get('PORT', 5000)),
    'demo_mode': os.environ.get('DEMO_MODE', None),

    # Exchange settings
    'domain': os.environ.get('OUTLOOK_DOMAIN', None),
    'ews_url': os.environ.get('OUTLOOK_EWS_URL', None),  # EWS = Exchange Web Services
    'username': os.environ.get('OUTLOOK_USERNAME', None),
    'password': os.environ.get('OUTLOOK_PASSWORD', None),
    'room_dict': os.environ.get('OUTLOOK_ROOM_DICT', None),
    'room_search_term': os.environ.get('OUTLOOK_ROOM_SEARCH_TERM', None),
    'cache_time': os.environ.get('CACHE_TIME', 30),

    # Security settings
    'allowed_ips': [
        ip.strip()
        for ip in _allowed_ips.split(',')
    ] if _allowed_ips else [],

    # Frontend settings
    'poll_interval': os.environ.get('OUTLOOK_POLL_INTERVAL', 1),
    'poll_start_minute': os.environ.get('OUTLOOK_POLL_START_MINUTE', 420),
    'poll_end_minute': os.environ.get('OUTLOOK_POLL_END_MINUTE', 1140),

    # InstaBook settings
    'instabook_times': [
        int(ib_time.strip())
        for ib_time in _instabook_times.split(',')
    ] if _instabook_times else [15, 30],
}

DEMO_MODE = False
if config['demo_mode'] and config['demo_mode'].lower() == 'true':
    DEMO_MODE = True
if not config['domain']:
    DEMO_MODE = True

ROOM_DISPLAY_SERVICE = None
if DEMO_MODE:
    from service.room_display_demo import RoomDisplayDemo
    ROOM_DISPLAY_SERVICE = RoomDisplayDemo()
else:
    from service.room_display_exchange import RoomDisplayExchange
    ROOM_DISPLAY_SERVICE = RoomDisplayExchange(
        config['domain'],
        config['ews_url'],
        config['username'],
        config['password'],
        config['room_dict'],
        config['room_search_term'],
        config['cache_time'],
    )


##################################################
#                    Serving
##################################################

@app.before_request
def restrict_access():
    client_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if config['allowed_ips'] and client_address not in config['allowed_ips']:
        sys.stderr.write('Insecure access blocked from {ip}!\n'.format(ip=client_address))
        abort(403)


@app.route('/')
def index():
    return flask.send_file('./templates/index.html')


@app.route('/data')
def data():
    # Get booking info from the room display service
    start = datetime.today().replace(hour=0, minute=0, second=0)
    end = datetime.today().replace(hour=23, minute=59, second=59)
    data = {
        'polling': {
            'interval': config['poll_interval'],
            'start_minute': config['poll_start_minute'],
            'end_minute': config['poll_end_minute'],
            'instabook_times': config['instabook_times'],
        },
        'rooms': ROOM_DISPLAY_SERVICE.get_room_data(start, end)
    }
    return jsonify(data)


@app.route('/instabook', methods=['POST'])
def instabook():
    # Extract POST data
    room_id = request.form['room_id']
    length = int(request.form['length'])

    # Check the room is free right now
    # TODO

    # Check the length is a valid one
    # TODO

    # Add a new booking
    ROOM_DISPLAY_SERVICE.add_booking(room_id, length)

    # Return something useful
    return jsonify({'success': True})


##################################################
#                    Main
##################################################

manager = Manager(app)

# Bind the dev server to 0.0.0.0 so it works through Docker
#manager.add_command('runserver', Server(host='0.0.0.0'))

@manager.command
def runserver():
    """
    Run the server
    """
    # Go go go
    print(
        'Running on port {HOST}:{PORT}'.format(
            HOST=config['host'],
            PORT=config['port']
        )
    )
    app.run(host=config['host'], port=config['port'])

@manager.command
def production():
    """
    Run the server in production mode
    """
    # Turn off debug on live...
    app.debug = False

    runserver()


if __name__ == '__main__':
    manager.run()
