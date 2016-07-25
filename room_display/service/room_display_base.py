from abc import ABCMeta, abstractmethod
import datetime
import logging

logger = logging.getLogger(__name__)


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
    def get_room_data(self):
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

        logger.debug(
            'Adding booking for "{room_id}" from {start} to {end}...'.format(#
                room_id=room_id,
                start=start,
                end=end,
            )
        )

        # Check the room is free right now
        if not self._is_free(room_id, start, end):
            return {'success': False, 'message': 'The room is not free for that booking!'}

        # Work out some more stuff
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

        logger.debug(
            'Adding booking for "{room_id}" from {start} to {end} done!'.format(#
                room_id=room_id,
                start=start,
                end=end,
            )
        )

        return {'success': True}

    @abstractmethod
    def _is_free(self, room_id, start, end):
        pass

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
