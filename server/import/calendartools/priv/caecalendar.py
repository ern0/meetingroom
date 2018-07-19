from icalendar import Calendar
from datetime import datetime, date
from .caecalendardata import CAECalendarData

class CAECalendar(Calendar):
    '''Calendar representation and basic querry functions'''

    def __init__(self):
        Calendar(self)

    def get_date_component(self, dt):
        ''' Return date part of datetime types'''
        if type(dt) is datetime:
            return dt.date()
        if type(dt) is date:
            return dt
        else:
            raise TypeException('{} is not a date type.'.format(dt))

    def get_events(self, calendar):
        ''' Return all events from calendar'''
        return calendar.walk('VEVENT')

    def get_events_by_date(self, day:date, calendar:Calendar):
        '''Return all events on a specific day'''
        results = []
        for event in CAECalendar().get_events(calendar):
            #start and end date is sometimes stored as date (all day event)
            #sometimes stored as datetime. For this comparism we use the date
            #component only.
            start_date = CAECalendar().get_date_component(event.get('dtstart').dt)
            end_date = CAECalendar().get_date_component(event.get('dtend').dt)

            if start_date <= day <= end_date: # Check if evetn is 'active' at a
                                              # given date.
                results.append(event)
        return results

    def get_active_events(self, calendar):
        '''return today events'''
        today = date.today()
        return CAECalendar().get_events_by_date(today, calendar)
