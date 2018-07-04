from icalendar import Calendar
from datetime import datetime, date
input json
template ='''
{
  "mapping": [
    {
      "room": "kilo",
      "input": "kilo.ics",
      "output": "/tmp/meetingroom/b-agenda-kilo.json"
    }
  ],
  "production": false,
  "date": "2018-07-04"
}
'''
class AgendaItem(object):
    def __init__(self, rawEvent):
        self.begin = '"{}T{}:{}"'.format(
            rawEvent.get('dtstart').dt.date()
            ,rawEvent.get('dtstart').dt.hour
            ,str(rawEvent.get('dtstart').dt.minute).zfill(2)
            )
        self.end = '"{}T{}:{}"'.format(
            rawEvent.get('dtend').dt.date()
            ,rawEvent.get('dtend').dt.hour
            ,str(rawEvent.get('dtend').dt.minute).zfill(2)
            )
        self.desc = '"{}"'.format(rawEvent.get('summary'))

    def __str__(self):
        return "{} {} {}".format(self.begin, self.end, self.desc)

    def reprJSON(self):
        return '''
        {{
            "begin": {},
            "end": {},
            "desc": {}
        }}'''.format(
        self.begin
        ,self.end
        ,self.desc
        )

class CAECalendarData(object):
    def __init__(self, room:str, date:str):
        self.room = room
        self.date = date
        self.agenda = []
    def addEvent(self, event:AgendaItem):
        self.agenda.append(event)

    def reprJSON(self):
        event_list = ',\n'.join([a.reprJSON() for a in self.agenda])
        return '''
        {{
            "agenda":
            [
            {}
            ],
            "room": "{}",
            "date": "{}"
        }}'''.format(
        event_list
        ,self.room
        ,self.date
        )

class CAECalendar(Calendar):
    def __init__(self):
        Calendar(self)

    '''Static class for querrying calendar events'''
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

if __name__ == "__main__":
    with open('november.ics','rb') as data: # Open test data ics file.
        calendar = Calendar.from_ical(data.read()) # Parse test data as ical.
        search_date = date(year=2017, month=2, day=22) # Define querry date.
        todayData = CAECalendarData('kilo', '2017-02-22')
        events = CAECalendar().get_events_by_date(day=search_date, calendar=calendar)
        for event in CAECalendar().get_events_by_date(day=search_date, calendar=calendar):
            todayData.addEvent(AgendaItem(event))
            todayData.addEvent(AgendaItem(event))
        print(todayData.reprJSON())
