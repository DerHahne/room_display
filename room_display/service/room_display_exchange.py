from datetime import datetime

from memoize import Memoizer

from service.exchange import ExchangeCalendar
from service.room_display_base import RoomDisplayBase


class RoomDisplayExchange(RoomDisplayBase):
    def __init__(
        self,
        domain,
        ews_url,
        username,
        password,
        room_dict,
        room_search_term,
        cache_time
    ):
        self.id_namespace = ".".join(reversed(ews_url.split('//', 1)[1].split('/')[0].split('.')))

        self.exchange = ExchangeCalendar(
            domain,
            ews_url,
            username,
            password
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

        # Apply caching
        if cache_time:
            store = {}
            memo = Memoizer(store)
            self.get_room_data = memo(max_age=cache_time)(self.get_room_data)

    def _check_room(self, room_email):
        start = datetime.today().replace(hour=0, minute=0, second=0)
        end = datetime.today().replace(hour=23, minute=59, second=59)

        try:
            # Fetch the room bookings
            self.exchange.get_bookings(start, end, room_email)
        except RuntimeError:
            return False
        return True

    def get_room_data(self, start, end):
        print('Fetching data from Exchange...')
        rooms = []

        for room_name, room_email in self.rooms.iteritems():
            meeting_room_details = {
                "id": "{}.{}".format(self.id_namespace, room_email.split('@')[0]),
                "name": room_name,
                "description": None,
                "bookings": [
                    self._transform_booking_info(booking)
                    for booking in self.exchange.get_bookings(start, end, room_email)
                ]
            }
            rooms.append(meeting_room_details)

        return rooms

    def _transform_booking_info(self, booking):
        start = booking.pop('start')
        end = booking.pop('end')
        booking.pop('description')

        booking['start_minute'] = self.datetime_to_minute(start)
        booking['end_minute'] = self.datetime_to_minute(end)

        return booking

    def _add_booking(
            self,
            room_id,
            start,
            end,
            subject,
            description
        ):
        # Add the booking
        self.exchange.add_booking(
            room_id,
            start,
            end,
            subject,
            description
        )

        # Invalidate the cache so the next data call will include the new booking
        self.get_room_data.delete()
