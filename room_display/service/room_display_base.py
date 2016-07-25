from abc import ABCMeta, abstractmethod


class RoomDisplayBase(object):
    __metaclass__ = ABCMeta

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
