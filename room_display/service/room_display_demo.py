from service.room_display_base import RoomDisplayBase


class RoomDisplayDemo(RoomDisplayBase):
    def __init__(self):
        self.rooms = {
            'room_awesome': {
                'id': 'room_awesome',
                'name': 'Awesome Room',
                'description': '10, Display, Aircon, Wifi, Cats',
                'bookings': [
                    {
                        'username': 'Alice',
                        'description': 'Innovation day brainstorm',
                        'start_minute': 540,
                        'end_minute': 570
                    },
                    {
                        'username': 'Bob',
                        'description': 'Lunch',
                        'start_minute': 840,
                        'end_minute': 900
                    },
                    {
                        'username': 'Alice',
                        'description': '<Private>',
                        'start_minute': 1020,
                        'end_minute': 1080
                    }
                ]
            },
            'room_boring': {
                'id': 'room_boring',
                'name': 'Boring Room',
                'description': '4',
                'bookings': [
                    {
                        'username': 'Eve',
                        'description': 'Innovation day brainstorm',
                        'start_minute': 540,
                        'end_minute': 1020
                    }
                ]
            }
        }

    def get_room_data(self, start, end):
        return self.rooms.values()

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
                'start_minute': self.datetime_to_minute(start),
                'end_minute': self.datetime_to_minute(end)
            }
        )
