from .agendaitem import AgendaItem

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
