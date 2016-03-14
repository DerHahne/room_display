from memoize import Memoizer

from service.exchange import ExchangeCalendar


class RoomDisplay(object):
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
            self.rooms = json.loads(room_dict)
        elif room_search_term:
            self.rooms = {room['displayName']: room['email'] for room in exchange.get_contacts(room_search_term)}
        else:
            raise Exception('You must provide one of room_dict or room_search_term!')

        # Apply caching
        if cache_time:
            store = {}
            memo = Memoizer(store)
            self.get_room_data = memo(max_age=cache_time)(self.get_room_data)

    def get_room_data(self, start, end, id_namespace):
        rooms = []

        for room_name, room_email in self.rooms.iteritems():
            print room_name, room_email
            meeting_room_details = {
                "id": "{}.{}".format(id_namespace, room_email.split('@')[0]),
                "name": room_name,
                "description": None,
                "bookings": [
                    _transform_booking_info(booking)
                    for booking in exchange.get_bookings(start, end, room_email)
                ]
            }
            rooms.append(meeting_room_details)

        return rooms

    def _transform_booking_info(self, booking):
        start = booking.pop('start')
        end = booking.pop('end')
        booking.pop('description')

        booking['start_minute'] = start.hour * 60 + start.minute
        booking['end_minute'] = end.hour * 60 + end.minute

        return booking
