from icalendar import Calendar
from datetime import datetime, date
import json

class AgendaItem(object):
    '''Plain old data class to store agenda items.'''

    def __init__(self, rawEvent):
        '''Initialize data class'''
        # Store begin date and time in format 'YYYY-MM-DDTHH:MM'.
        self.begin = '"{}T{}:{}"'.format(
            rawEvent.get('dtstart').dt.date()
            ,rawEvent.get('dtstart').dt.hour
            ,str(rawEvent.get('dtstart').dt.minute).zfill(2)
        )

        # Store end date and time in format 'YYYY-MM-DDTHH:MM'.
        self.end = '"{}T{}:{}"'.format(
            rawEvent.get('dtend').dt.date()
            ,rawEvent.get('dtend').dt.hour
            ,str(rawEvent.get('dtend').dt.minute).zfill(2)
        )

        # Store description.
        self.desc = '"{}"'.format(rawEvent.get('summary'))

    def reprJSON(self):
        '''Make the class JSON serializable'''
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
    '''This data class stores basic information about the meeting room'''

    def __init__(self, room:str, date:str):
        '''Initialize data class'''
        self.room = room
        self.date = date
        self.agenda = []

    def addEvent(self, event:AgendaItem):
        '''Appends an event to the event list'''
        self.agenda.append(event)

    def reprJSON(self):
        '''Make the class JSON serializable'''
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

class ICalFetcher:
    '''This class reads JSON requests and returns the JSON representation of
    a given ical file.'''

    def file_fetch(self, ifile):
        '''Takes the JSON request file and returns the JSON calendar representation.'''
        with open(ifile, 'r') as input:
            request = input.read()
            ICalFetcher().fetch(request)

    def fetch(self, request):
        '''Takes the JSON request and returns the JSON calendar representation.'''

        json_input = json.loads(request)

        for mapping in json_input['mapping']:
            #Loop all mappings(~sub-requests) in the original JSON requests
            ics_input = mapping['input']
            json_output = mapping['output']
            #Parse events from ics file.
            events = ICalFetcher().__parse_ics(ics_input, json_input['date'])
            #Create CAECalendarData instance to store ics elements.
            calendar_data = CAECalendarData(
                ics_input
                ,json_input['date']
            )
            # Stor events in the calendar data class.
            for event in events:
                calendar_data.addEvent(AgendaItem(event))

            ICalFetcher().__dumps(calendar_data, json_output)


    def __parse_ics(self, ics, date_str):
        '''Parse ics file and return event list.'''

        with open(ics) as calendar_file:
            calendar = Calendar.from_ical(calendar_file.read())
            return CAECalendar().get_events_by_date(
                ICalFetcher().__date_str_to_date(date_str)
                , calendar
            )

    def __date_str_to_date(self, date_str):
        '''create date object form string (format "YYYY-MM-DD")'''
        year, month, day = date_str.split('-')
        return date(
            year=int(year)
            , month=int(month)
            , day=int(day)
        )

    def __dumps(self, calendar_data, json_output):
        '''Dump to output JOSN file.'''
        with open(json_output,'w') as ofile:
            json_repr = json.loads(calendar_data.reprJSON())
            json.dump(json_repr, ofile)


if __name__ == "__main__":
    ''' Basic test of functionality'''
    test_request ='''
    {
      "mapping": [
        {
          "room": "november",
          "input": "november.ics",
          "output": "/tmp/meetingroom/b-agenda-kilo.json"
        }
      ],
      "production": false,
      "date": "2017-02-22"
    }
    '''
    ICalFetcher().fetch(test_request)
