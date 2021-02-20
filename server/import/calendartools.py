from icalendar import Calendar
from datetime import datetime, date

class CalendarTools:
    '''Static class for querrying calendar events'''
    def get_date_component(dt):
        ''' Return date part of datetime types'''
        if type(dt) is datetime:
            return dt.date()
        if type(dt) is date:
            return dt
        else:
            raise TypeException('{} is not a date type.'.format(dt))

    def get_events(calendar):
        ''' Return all events from calendar'''
        return calendar.walk('VEVENT')

    def get_events_by_date(day:date, calendar:Calendar):
        '''Return all events on a specific day'''
        results = []
        for event in CalendarTools.get_events(calendar):
            #start and end date is sometimes stored as date (all day event)
            #sometimes stored as datetime. For this comparism we use the date
            #component only.
            start_date = CalendarTools.get_date_component(event.get('dtstart').dt)
            end_date = CalendarTools.get_date_component(event.get('dtend').dt)

            if start_date <= day <= end_date: # Check if evetn is 'active' at a
                                              # given date.
                results.append(event)
        return results

    def get_active_events(calendar):
        '''return today events'''
        today = date.today()
        return CalendarTools.get_events_by_date(today, calendar)

'''
TEST
'''
with open('november.ics','rb') as data: # Open test data ics file.
    calendar = Calendar.from_ical(data.read()) # Parse test data as ical.
    search_date = date(year=2017, month=2, day=22) # Define querry date.
    events = CalendarTools.get_events_by_date(day=search_date,calendar=calendar)
    for event in events:
        print('{} :: {}'.format(event.get('summary'), event.get('dtstart').dt))
