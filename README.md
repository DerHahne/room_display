# Room Display

A service to allow easy display of meeting room status from Outlook/Exchange on a web based tablet interface

![Room Display](https://github.com/csudcy/room_display/blob/master/images/room_display.gif)

## Running

### Docker

The easiest way to run the server is using [docker-compose](https://docs.docker.com/compose/):
```bash
cp config.env.template config.env
vi config.env
# Update environment variables (see below)
docker-compose up
```
Once the image has finished building & everything is running, you should be able to hit [http://192.168.99.100:5000] to view the website.

### Heroku

[Heroku](https://www.heroku.com/) should automatically work via the `Procfile`

### Cloud9

To run on [Cloud9](https://c9.io/) (and possibly Debian based Linux in general):
```bash
sudo apt-get install python-lxml
sudo pip install -r requirements.txt
python room_display/app.py runserver
```


## Settings

The following environment variables can be set (all are optional):
* Server settings:
  * `IP`: The IP to bind the web server to (defaults to `0.0.0.0`)
  * `PORT`: The port to bind the web server to (defaults to `5000`)
* Misc settings:
  * `DEMO_MODE`: If this is set to `"true"`, the server will operate in a demonstration mode (using example data)
  * `INSTABOOK_TIMES`: A comma separated list of meeting lengths allowed by Insta-booking
* Exchange settings:
  * `OUTLOOK_DOMAIN`: Domain for the outlook user to log onto
    * If this is left blank, demo mode will be enabled
  * `OUTLOOK_EWS_URL`: URL to the EWS endpoint on the exchange server e.g. [https://<your exchange server>/EWS/Exchange.asmx]
  * `OUTLOOK_USERNAME`: User for exchange
  * `OUTLOOK_PASSWORD`: Password for exchange
  * `OUTLOOK_ROOM_DICT` (See below): A JSON dump of a dict containing the room name as a key and the room's email address as a value
  * `OUTLOOK_ROOM_SEARCH_TERM` (See below): A string fragment to match to find contacts that are meeting rooms from the exchange global address list
  * `OUTLOOK_REFRESH_TIME`: How often to grab the data from Exchange
  * `OUTLOOK_TIMEZONE_NAME`: What timezone the Exchange server is in e.g. `Europe/London`
* Security settings:
  * `ALLOWED_IPS`: A comma separated listed of allowed IPs. Default is allowed by any IP.
* Frontend settings:
  * `POLL_INTERVAL`: Poll wait time for the client in minutes. Defaults to 1.
  * `POLL_START_MINUTE`: Poll start time in minutes from midnight. Defaults to 420 (7am)
  * `POLL_END_MINUTE`: Poll end time in minutes from midnight. Defaults to 1140 (7pm).

Either the list of meeting rooms must be supplied as a json.dumps string:
```python
json.dumps({'Meeting Room A': 'room.mtg.a@example.com', 'Meeting Room B': 'room.mtg.b@example.com'})
```
OR you can set the search term to a fragment of a meeting room name and let the app find the meeting rooms for itself. E.g.:
If the meeting rooms are called "Cloud Meet", "Corporate Meet" and "Blue Meet" then the search term should be "Meet".


## Todo

Backend:
* InstaBooking:
  * Booking takes a while to showup; maybe add it to the booking list rather than refreshing?
  * Only refresh bookings for the room which has been updated
  * Check if the room is free
* Store the data we get from outlook when `_check_room` is run
* Add makefile?

Frontend:
* InstaBooking:
  * Show a confirmation dialog
  * Let the user know if there was an error booking
* Click on room in dashboard
  * Make it work when there are no bookings
  * Make the tick/cross clickable
* Fix dashboard updating - Angular doesnt seem to pickup when `first_booking` is changed?
* Add home page & move there after inactivity
* Add currently free room suggestions
* Add soonest free room suggestions

Extra ideas:
* Move to timestamps instead of minutes (to support multi-day meetings)
* Theme switching with https://github.com/jguadagno/bootstrapThemeSwitcher
* Room locations
* eInk/RaspberryPi Display
* Room facilities & icons
* Mulitple backends


## Credits

* [Angular](https://angularjs.org/)
* [Bootstrap](http://getbootstrap.com/)
* [BootstrapCDN](https://www.bootstrapcdn.com/) for bootstrap theme hosting
* [Bootswatch](https://bootswatch.com/)
* [cdnjs](https://cdnjs.com/) for library hosting
* [Flask](http://flask.pocoo.org/)
* [IconArchive](http://www.iconarchive.com/show/pretty-office-7-icons-by-custom-icon-design/Calendar-icon.html) for the favicon
* [jQuery](https://jquery.com/)
