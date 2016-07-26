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
        self.refresh_time_seconds = refresh_time_seconds
        self.timezone = timezone(timezone_name)
        self.exchange = ExchangeCalendar(
            domain,
            ews_url,
            username,
            password,
            self.timezone
        )

        # Find the rooms
        potential_rooms = self._get_potential_rooms(room_dict, room_search_term)
        self.rooms = self._get_valid_rooms(potential_rooms)

        # Start the data grabbing thread
        Thread.__init__(self)
        self.start()

    def _magic_timezone_conversion(self, dt):
        # Yay, timezones!
        return timezone('UTC').localize(dt).astimezone(self.timezone)

    def _get_day_boundaries(self):
        now = self._magic_timezone_conversion(datetime.now())
        start = now.replace(hour=0, minute=0, second=0)
        end = now.replace(hour=23, minute=59, second=59)
        return start, end

    def _get_potential_rooms(self, room_dict, room_search_term):
        if room_dict:
            return json.loads(room_dict)
        if room_search_term:
            return {
                room['displayName']: room['email']
                for room in self.exchange.get_contacts(room_search_term)
            }
        raise Exception('You must provide one of room_dict or room_search_term!')

    def _get_valid_rooms(self, potential_rooms):
        rooms = {}
        for room_name, room_email in potential_rooms.iteritems():
            try:
                # Try to fetch the room bookings
                rooms[room_email] = {
                    'id': room_email,
                    'name': room_name,
                    'bookings': self._get_bookings(room_email)
                }
            except RuntimeError:
                # Couldn't get the bookings; skip this room
                pass
        return rooms

    def _get_bookings(self, room_id):
        start, end = self._get_day_boundaries()
        return [
            self._transform_booking_info(booking)
            for booking in self.exchange.get_bookings(start, end, room_id)
        ]

    def _transform_booking_info(self, booking):
        return {
            'username': booking['username'],
            'start_minute': self.datetime_to_minute(booking['start']),
            'end_minute': self.datetime_to_minute(booking['end']),
        }

    def run(self):
        logger.debug('Data thread: Starting...')
        while (True):
            logger.debug('Data thread: Waiting...')
            time.sleep(self.refresh_time_seconds)
            logger.debug('Data thread: Fetching...')
            self._update_rooms()
        logger.debug('Data thread: Done!')

    def _update_rooms(self):
        for room_id in self.rooms.iterkeys():
            self._update_room(room_id)

    def _update_room(self, room_id):
        self.rooms[room_id]['bookings'] = self._get_bookings(room_id)

    def get_room_data(self):
        return self.rooms.values()

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

        # Wait a bit to let Exchange work out what's going on
        time.sleep(5)

        # Get the latest Exchange data now
        self._update_room(room_id)
