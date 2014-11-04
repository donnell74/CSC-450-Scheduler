from __future__ import print_function
import structures
from copy import copy


class Room:

    """A particular room, consisting of a room number and a list of time slot objects"""
    def __init__(self, building, number, this_day, test = False):
        if test:
            self.day = this_day
        else:
            self.day = copy(this_day)
        
        self.building = building
        self.number = number

        time_slots_mwf = self.info("Schedule").time_slots_mwf

        if self.day.day_code in 'tr':
            time_slots_tr = self.info("Schedule").time_slots_tr
        else:
            time_slots_tr = []

        # list of time slot objects
        self.schedule = self.generate_time_slots(time_slots_mwf, time_slots_tr)  

    def info(self, query):
        """Goes up the object hierarchy to find object for given room
        Possible queries: Day, week, schedule
        IN: query string
        OUT: object of query's type for given room"""
        if query not in ["Day", "Week", "Schedule"]:
            print("Invalid query for Room")
            return
        elif query == "Day":
            return self.day
        elif query == "Week":
            return self.day.week
        elif query == "Schedule":
            return self.day.week.schedule

    def generate_time_slots(self, time_slots_mwf, time_slots_tr):
        this_schedule = []
        for each_slot in time_slots_mwf:
            start, end = each_slot.split('-')
            this_schedule.append(
                structures.TimeSlot(start.split(':'), end.split(':'), self, isTR=False))

        for each_slot in time_slots_tr:
            start, end = each_slot.split('-')
            this_schedule.append(
                structures.TimeSlot(start.split(':'), end.split(':'), self, isTR=True))

        return this_schedule

    def __str__(self):
        #return "\n".join([str(i) for i in self.schedule])
        return str(self.building) + " " + str(self.number) # + "\n"  + "\n".join([str(t) for t in self.schedule])

    def __iter__(self):
        for t_slot in self.schedule:
            yield t_slot

    def __eq__(self, other):
        return self.building == other.building and\
               self.number == other.number
