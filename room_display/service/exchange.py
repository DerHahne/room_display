import logging

from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from pyexchange.exceptions import (FailedExchangeException, ExchangeStaleChangeKeyException,
                                   ExchangeItemNotFoundException, ExchangeIrresolvableConflictException,
                                   ExchangeInternalServerTransientErrorException)
from pyexchange.exchange2010 import Exchange2010CalendarEvent
from pyexchange.exchange2010 import soap_request

logger = logging.getLogger(__name__)


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
    def __init__(self, domain, url, username, password, timezone):
        super(ExchangeCalendar, self).__init__()

        self.timezone = timezone

        connection = ExchangeNTLMAuthConnection(
            url=url,
            username='%s\\%s' % (domain, username),
            password=password
        )
        self._service = Exchange2010Service(connection)
        self.calendar = self._service.calendar()

    def get_bookings(self, start, end, email_address):
        logger.debug(
            'Getting bookings for {email_address} from {start} to {end}...'.format(
                start=start.isoformat(),
                end=end.isoformat(),
                email_address=email_address
            )
        )

        try:
            return [
                self._calendar_event_to_dict(event)
                for event in
                self.calendar.list_events(
                    start=start,
                    end=end,
                    details=False,
                    delegate_for=email_address
                ).events
            ]
        except FailedExchangeException as ex:
            raise RuntimeError(str(ex))
        finally:
            logger.debug(
                'Getting bookings for {email_address} from {start} to {end} done!'.format(
                    start=start.isoformat(),
                    end=end.isoformat(),
                    email_address=email_address
                )
            )

    def _calendar_event_to_dict(self, event):
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
            'start': event.start.astimezone(self.timezone),
            'end': event.end.astimezone(self.timezone),
        }

    def get_contacts(self, search):
        return self._service.contacts().search_contacts(search).contacts

    def add_booking(
            self,
            room_email,
            start,
            end,
            subject,
            description
        ):
        # TODO: Use a nicer location than the rooms email address

        # Create the event
        event = self.calendar.new_event(
            resources=[room_email],
            location=room_email,
            start=self.timezone.localize(start),
            end=self.timezone.localize(end),
            subject=subject,
            html_body=description
        )

        # Connect to Exchange and create the event
        event.create()
