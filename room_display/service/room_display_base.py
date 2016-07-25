from abc import ABCMeta, abstractmethod
import datetime


class RoomDisplayBase(object):
    __metaclass__ = ABCMeta

    INSTABOOK_SUBJECT = u'Insta-Booking ({length})'
    INSTABOOK_DESCRIPTION = u"""
    <html>
        <body>
            <h1>{subject}</h1>
            <p>This is an Insta-Booking by <a href="https://github.com/csudcy/room_display">Room Display</a></p>
        </body>
    </html>"""

    @staticmethod
    def datetime_to_minute(dt):
        return dt.hour * 60 + dt.minute

    @abstractmethod
    def get_room_data(self, start, end):
        """
        Get a list of dictionaries with room information in.
        For example:
        [
            {
                "id": "room_boring",
                "name": "Boring Room",
                "description": "4",
                "bookings": [
                    {
                        "username": "Eve",
                        "description": "Innovation day brainstorm",
                        "start_minute": 540,
                        "end_minute": 1020
                    },
                    ...
                ]
            },
            ...
        ]
        """
        pass

    def add_booking(self, room_id, length):
        # Work out some stuff
        start = datetime.datetime.now()
        end = start + datetime.timedelta(minutes=length)
        subject = self.INSTABOOK_SUBJECT.format(
            length=length
        )
        description = self.INSTABOOK_DESCRIPTION.format(
            subject=subject
        )

        # Pass through to the implementation specific method
        self._add_booking(
            room_id,
            start,
            end,
            subject,
            description
        )

    @abstractmethod
    def _add_booking(
            self,
            room_id,
            start,
            end,
            subject,
            description
        ):
        pass
