from icalendar import Calendar
from datetime import datetime, date
import json
from priv.caecalendar import CAECalendar
from priv.caecalendardata import CAECalendarData
from priv.agendaitem import AgendaItem

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
                mapping['room']
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
          "input": "test/november.ics",
          "output": "test/test2.json"
        }
      ],
      "production": false,
      "date": "2017-02-22"
    }
    '''
    test_request2 ='''
    {
      "mapping": [
        {
          "room": "test",
          "input": "test/gcal-sample.txt",
          "output": "test/test.json"
        }
      ],
      "production": false,
      "date": "2018-07-03"
    }
    '''
    ICalFetcher().fetch(test_request)
    ICalFetcher().fetch(test_request2)
