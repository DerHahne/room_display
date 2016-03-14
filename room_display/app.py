import json
import os
from datetime import datetime

import flask
from flask import Flask, jsonify, abort, request
from flask_heroku import Heroku
from flask_script import Manager
from flask_script import Server

from service.room_display import RoomDisplay


##################################################
#                    Setup
##################################################

app = Flask(__name__)
app.debug = True
heroku = Heroku(app)

_allowed_ips = os.environ.get('OUTLOOK_ALLOWED_IPS', '')

config = {
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
}

ROOM_DISPLAY_SERVICE = None
if config['domain']:
    ROOM_DISPLAY_SERVICE = RoomDisplay(
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
    if config['allowed_ips'] and request.remote_addr not in config['allowed_ips']:
        abort(403)


@app.route('/')
def index():
    return flask.send_file('./templates/index.html')


@app.route('/data')
def data():
    # If there is no domain, return the example data
    if not ROOM_DISPLAY_SERVICE:
        return flask.send_file('../example_data.json')

    # Otherwise, get the info from Exchange
    start = datetime.today().replace(hour=7, minute=0, second=0, microsecond=0)
    end = datetime.today().replace(hour=23, minute=0, second=0, microsecond=0)
    data = {
        "polling": {
            "interval": config['poll_interval'],
            "start_minute": config['poll_start_minute'],
            "end_minute": config['poll_end_minute'],
        },
        "rooms": ROOM_DISPLAY_SERVICE.get_room_data(start, end)
    }
    return jsonify(data)


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
