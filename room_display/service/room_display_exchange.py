from datetime import datetime
from threading import Thread
import logging
import time

from pytz import timezone

from service.exchange import ExchangeCalendar
from service.room_display_base import RoomDisplayBase

logger = logging.getLogger(__name__)


class RoomDisplayExchange(RoomDisplayBase, Thread):
    def __init__(
        self,
        domain,
        ews_url,
        username,
        password,
        room_dict,
        room_search_term,
        refresh_time_seconds,
        timezone_name,
    ):
        self.timezone = timezone(timezone_name)
        self.exchange = ExchangeCalendar(
            domain,
            ews_url,
            username,
            password,
            self.timezone
        )

        if room_dict:
            potential_rooms = json.loads(room_dict)
        elif room_search_term:
            potential_rooms = {room['displayName']: room['email'] for room in self.exchange.get_contacts(room_search_term)}
        else:
            raise Exception('You must provide one of room_dict or room_search_term!')

        # Check for valid rooms
        self.rooms = dict([
            (room_name, room_email)
            for room_name, room_email in potential_rooms.iteritems()
            if self._check_room(room_email)
        ])

        # Start the data grabbing thread
        self._rooms = []
        self.refresh_time_seconds = refresh_time_seconds
        Thread.__init__(self)
        self.start()

    def run(self):
        logger.debug('Data thread: Starting...')
        while (True):
            logger.debug('Data thread: Fetching...')
            self._update_room_data()
            logger.debug('Data thread: Waiting...')
            time.sleep(self.refresh_time_seconds)
        logger.debug('Data thread: Done!')

    def _magic_timezone_conversion(self, dt):
        # Yay, timezones!
        return timezone('UTC').localize(dt).astimezone(self.timezone)

    def _get_day_boundaries(self):
        now = self._magic_timezone_conversion(datetime.now())
        start = now.replace(hour=0, minute=0, second=0)
        end = now.replace(hour=23, minute=59, second=59)
        return start, end

    def _check_room(self, room_email):
        start, end = self._get_day_boundaries()

        try:
            # Fetch the room bookings
            self.exchange.get_bookings(start, end, room_email)
        except RuntimeError:
            return False
        return True

    def _update_room_data(self):
        start, end = self._get_day_boundaries()

        rooms = []

        for room_name, room_email in self.rooms.iteritems():
            meeting_room_details = {
                'id': room_email,
                'name': room_name,
                'bookings': [
                    self._transform_booking_info(booking)
                    for booking in self.exchange.get_bookings(start, end, room_email)
                ]
            }
            rooms.append(meeting_room_details)

        self._rooms = rooms

    def get_room_data(self):
        return self._rooms

    def _transform_booking_info(self, booking):
        return {
            'username': booking['username'],
            'start_minute': self.datetime_to_minute(booking['start']),
            'end_minute': self.datetime_to_minute(booking['end']),
        }

    def _is_free(self, room_id, start, end):
        # TODO: Work this out!
        return True

    def _add_booking(
            self,
            room_id,
            start,
            end,
            subject,
            description
        ):
        start = self._magic_timezone_conversion(start)
        end = self._magic_timezone_conversion(end)

        # Add the booking
        self.exchange.add_booking(
            room_id,
            start,
            end,
            subject,
            description
        )

        # Get the latest Exchange data now
        self._update_room_data()
