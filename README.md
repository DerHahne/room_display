# Room Display

A service to allow easy display of meeting room status from Outlook/Exchange on a web based tablet interface


## Running

The easiest way to run the server is using docker-compose:
```bash
docker-compose up
```
Once the image has finished building & everything is running, you should be able to hit http://192.168.99.100:5000 to view the website.


## Settings

The following environment variables need to be set for the app to work:
* OUTLOOK_DOMAIN: Domain for the outlook user to log onto
* OUTLOOK_EWS_URL: URL to the EWS endpoint on the exchange server
* OUTLOOK_USERNAME: User for exchange
* OUTLOOK_PASSWORD: Password for exchange
* [See below] OUTLOOK_ROOM_DICT: A json.dumps of a dict containing the room name as a key and the room's email address as a value
* [See below] OUTLOOK_ROOM_SEARCH_TERM: A string fragment to match to find contacts that are meeting rooms from the exchange global address list
* [Optional] OUTLOOK_POLL_INTERVAL: Poll wait time for the client in minutes. Defaults to 1.
* [Optional] OUTLOOK_POLL_START_MINUTE: Poll start time in minutes from midnight. Defaults to 420 (7am)
* [Optional] OUTLOOK_POLL_END_MINUTE: Poll end time in minutes from midnight. Defaults to 1140 (7pm).
* [Optional] OUTLOOK_ALLOWED_IPS: A comma separated listed of allowed IPs. Default is allowed by any IP.

Either the list of meeting rooms must be supplied as a json.dumps string:
```
json.dumps({'Meeting Room A': 'room.mtg.a@example.com', 'Meeting Room B': 'room.mtg.b@example.com'})
```
OR you can set the search term to a fragment of a meeting room name and let the app find the meeting rooms for itself. E.g.:
If the meeting rooms are called "Cloud Meet", "Corporate Meet" and "Blue Meet" then the search term should be "Meet".

## Todo

Backend:
* Add makefile?
* Return dummy data
* Periodically poll for new data
  * Accept interval as environment variable?
  * Accept poll times (i.e. 7am-7pm) as environment variable?

Frontend:
* Render overview page
* Render individual page
* Retrieve data from backend
* Periodically poll for new data
  * Follow same interval & times as backend?
* Add home page & move there after inactivity
* Add currently free room suggestions
* Add soonest free room suggestions

Extra ideas:
* Move to timestamps instead of minutes (to support multi-day meetings)
* Add insta-bookings
* Theme switching with https://github.com/jguadagno/bootstrapThemeSwitcher
* Security through obscurity?
  * Have a key which you have to enter the first time you go to the URL
  * Also allows multi-tenancy
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
