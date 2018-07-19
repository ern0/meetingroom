from icalendar import Calendar
from datetime import datetime, date

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
