from abc import ABCMeta, abstractmethod


class BaseCalendar(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._service = None
        self._calendar = None

    @property
    def calendar(self):
        if self._calendar is None:
            self._calendar = self.get_calendar()
        return self._calendar

    @abstractmethod
    def get_calendar(self):
        pass


