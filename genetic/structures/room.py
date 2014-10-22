from __future__ import print_function
import structures
from copy import copy


class Room:
    """A particular room, consisting of a room number and a list of time slot objects"""
    def __init__(self, building, number, this_day):
        self.day = copy(this_day)
        self.building = building
        self.number = number

        time_slots = self.info("Schedule").time_slots
        '''if self.day.day_code in 'mwf':
            time_slots = self.info("Schedule").time_slots_mwf
        else:
            time_slots = self.info("Schedule").time_slots_tr'''

        self.schedule = self.generate_time_slots(time_slots) #list of time slot objects

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

    def generate_time_slots(self, time_slots):
        this_schedule = []
        for each_slot in time_slots:
            start, end = each_slot.split('-')
            this_schedule.append(structures.TimeSlot(start.split(':'), end.split(':'), self))

        return this_schedule

    def __str__(self):
        return str(self.building) + " " + str(self.number) # + "\n"  + "\n".join([str(t) for t in self.schedule])

    def __iter__(self):
        for t_slot in self.schedule:
            yield t_slot


