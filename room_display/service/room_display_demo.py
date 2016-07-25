from service.room_display_base import RoomDisplayBase


class RoomDisplayDemo(RoomDisplayBase):
    def __init__(self):
        def booking(username, h, m, l):
            start_minute = h * 60 + m
            return {
                'username': username,
                'start_minute': start_minute,
                'end_minute': start_minute + l
            }
        self.rooms = {
            'red_room': {
                'id': 'red_room',
                'name': 'Red Room',
                'bookings': [
                    booking('Alice', 9, 15, 30),
                    booking('Bob', 10, 0, 120),
                    booking('Carol', 12, 0, 60),
                ]
            },
            'orange_room': {
                'id': 'orange_room',
                'name': 'Orange Room',
                'bookings': [
                    booking('Alice', 9, 45, 30),
                    booking('Bob', 11, 0, 120),
                    booking('Carol', 13, 0, 60),
                ]
            },
            'yellow_room': {
                'id': 'yellow_room',
                'name': 'Yellow Room',
                'bookings': [
                    booking('Alice', 10, 15, 30),
                    booking('Bob', 12, 0, 120),
                    booking('Carol', 14, 0, 60),
                ]
            },
            'green_room': {
                'id': 'green_room',
                'name': 'Green Room',
                'bookings': [
                    booking('Alice', 10, 45, 30),
                    booking('Bob', 13, 0, 120),
                    booking('Carol', 15, 0, 60),
                ]
            },
            'blue_room': {
                'id': 'blue_room',
                'name': 'Blue Room',
                'bookings': [
                    booking('Alice', 11, 15, 30),
                    booking('Bob', 14, 0, 120),
                    booking('Carol', 16, 0, 60),
                ]
            },
            'indigo_room': {
                'id': 'indigo_room',
                'name': 'Indigo Room',
                'bookings': [
                    booking('Alice', 11, 45, 30),
                    booking('Bob', 15, 0, 120),
                    booking('Carol', 17, 0, 60),
                ]
            },
            'violet_room': {
                'id': 'violet_room',
                'name': 'Violet Room',
                'bookings': [
                    booking('Alice', 12, 15, 30),
                    booking('Bob', 16, 0, 120),
                    booking('Carol', 18, 0, 60),
                ]
            },
        }

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
        self.rooms[room_id]['bookings'].append(
            {
                'username': 'InstaBooking',
                'description': subject,
                # TODO: Fix Timezone issues!
                'start_minute': self.datetime_to_minute(start) + 60,
                'end_minute': self.datetime_to_minute(end) + 60
            }
        )
        self.rooms[room_id]['bookings'].sort(key=lambda booking: booking['start_minute'])
