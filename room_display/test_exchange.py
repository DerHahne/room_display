from datetime import datetime, timedelta
from pytz import timezone

from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from pyexchange.exceptions import FailedExchangeException

class ExchangeService(object):
    def __init__(self, domain, url, calendar="calendar"):
        self._service = None
        self._calendar = None
        self._rooms = None
        self._calendar_name = calendar
        self._domain = domain
        self._url = url

    def connect(self, username, password):
        connection = ExchangeNTLMAuthConnection(url=self._url,
                                                username='%s\\%s' % (self._domain, username),
                                                password=password)
        self._service = Exchange2010Service(connection)
        self._calendar = self._service.calendar(id=self._calendar_name)
        self._rooms = self._service.rooms()

    def get_events(self):
        current_time = datetime.now()
        try:
            return [event for event in self._calendar.list_events(start=timezone("GMT").localize(current_time),
                    end=timezone("GMT").localize(current_time + timedelta(days=1)),
                    details=True).events]
        except FailedExchangeException as ex:
            raise RuntimeError(str(ex))

# Bigelow710
exchange = ExchangeService('aam', 'https://outlook.artsalliancemedia.com/EWS/Exchange.asmx')
exchange.connect('', '')

def stuff(item):
    """
    subject = u''
    start = None
    end = None
    location = None
    html_body = None
    text_body = None
    attachments = None
    organizer = None
    """
    return {
        'subject': item.subject,
        'location': item.location,
        'organizer': item.organizer,
        'description': item.text_body,
    }
#print(exchange._rooms.list_room_lists().roomLists)
print(exchange._rooms.list_rooms('mtg.bigelow@artsalliancemedia.com'))
#print([stuff(item) for item in exchange.get_events()])





