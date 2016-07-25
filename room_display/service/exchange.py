from pytz import timezone

from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from pyexchange.exceptions import (FailedExchangeException, ExchangeStaleChangeKeyException,
                                   ExchangeItemNotFoundException, ExchangeIrresolvableConflictException,
                                   ExchangeInternalServerTransientErrorException)
from pyexchange.exchange2010 import Exchange2010CalendarEvent
from pyexchange.exchange2010 import soap_request


# A monkey patching we do go
def non_borked_check_for_exchange_fault(self, xml_tree):
    response_codes = xml_tree.xpath(u'//m:ResponseCode', namespaces=soap_request.NAMESPACES)

    if not response_codes:
      raise FailedExchangeException(u"Exchange server did not return a status response", None)

    # The full (massive) list of possible return responses is here.
    # http://msdn.microsoft.com/en-us/library/aa580757(v=exchg.140).aspx
    for code in response_codes:
      if code.text == u"ErrorChangeKeyRequiredForWriteOperations":
        # change key is missing or stale. we can fix that, so throw a special error
        raise ExchangeStaleChangeKeyException(u"Exchange Fault (%s) from Exchange server" % code.text)
      elif code.text == u"ErrorItemNotFound":
        # exchange_invite_key wasn't found on the server
        raise ExchangeItemNotFoundException(u"Exchange Fault (%s) from Exchange server" % code.text)
      elif code.text == u"ErrorIrresolvableConflict":
        # tried to update an item with an old change key
        raise ExchangeIrresolvableConflictException(u"Exchange Fault (%s) from Exchange server" % code.text)
      elif code.text == u"ErrorInternalServerTransientError":
        # temporary internal server error. throw a special error so we can retry
        raise ExchangeInternalServerTransientErrorException(u"Exchange Fault (%s) from Exchange server" % code.text)
      elif code.text == u"ErrorCalendarOccurrenceIndexIsOutOfRecurrenceRange":
        # just means some or all of the requested instances are out of range
        pass
      elif code.text == u"ErrorNameResolutionMultipleResults":
        # This just means that we got more than one possible contact
        pass
      elif code.text != u"NoError":
        raise FailedExchangeException(u"Exchange Fault (%s) from Exchange server" % code.text)

Exchange2010Service._check_for_exchange_fault = non_borked_check_for_exchange_fault


class ExchangeCalendar(object):
    TIMEZONE = "GMT"

    def __init__(self, domain, url, username, password):
        super(ExchangeCalendar, self).__init__()

        connection = ExchangeNTLMAuthConnection(
            url=url,
            username='%s\\%s' % (domain, username),
            password=password
        )
        self._service = Exchange2010Service(connection)
        self.calendar = self._service.calendar()

    def get_bookings(self, start, end, email_address):
        try:
            return [
                self._calendar_event_to_dict(event)
                for event in
                self.calendar.list_events(
                    start=timezone(self.TIMEZONE).localize(start),
                    end=timezone(self.TIMEZONE).localize(end),
                    details=False,
                    delegate_for=email_address
                ).events
            ]
        except FailedExchangeException as ex:
            raise RuntimeError(str(ex))

    @staticmethod
    def _calendar_event_to_dict(event):
        if not isinstance(event, Exchange2010CalendarEvent):
            raise ValueError(
                '{} is not of type {}'.format(
                    type(event),
                    type(Exchange2010CalendarEvent)
                )
            )

        return {
            'username': event.organizer.name,
            'email_address': event.organizer.email,
            'subject': event.subject.strip(),
            'description': event.text_body,
            'start': event.start,
            'end': event.end,
        }

    def get_contacts(self, search):
        return self._service.contacts().search_contacts(search).contacts

    def add_booking(
            self,
            room_id,
            start,
            end,
            subject,
            description
        ):
        # TODO: Use a nicer location than the rooms email address

        # Create the event
        event = service.calendar.new_event(
            attendees=[room_id],
            location=room_id,
            start=timezone(self.TIMEZONE).localize(start),
            end=timezone(self.TIMEZONE).localize(end),
            subject=subject,
            html_body=description
        )

        # Connect to Exchange and create the event
        event.create()
