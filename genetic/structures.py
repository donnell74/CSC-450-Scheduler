from __future__ import print_function
from copy import deepcopy
from copy import copy
from datetime import time, timedelta
import logging
import random

class Day:
    """A particular day, consisting of a list of room objects"""
    def __init__(self, rooms, day_code, this_week):
        self.week = copy(this_week)
        if day_code.lower() in 'mtwrf':
            self.day_code = day_code
        else:
            logging.error("Day code was not recognized")
            print("Day code was not recognized")
            return
        self.rooms = [Room(number, self) for number in rooms]

    def info(self, query):
        """Goes up the object hierarchy to find object for given day
        Possible queries: week, schedule
        IN: query string
        OUT: object of query's type for given day"""
        if query not in ["Week", "Schedule"]:
            logging.error("Invalid query for Day")
            print("Invalid query for Day")
            return
        elif query == "Week":
            return self.week
        elif query == "Schedule":
            return self.week.schedule

    def __str__(self):
        return "-----------------------\n" + \
                "Day: " + self.day_code + '\n' + "Rooms:\n" + \
                "\n".join([str(r) for r in self.rooms])

class Room:
    """A particular room, consisting of a room number and a list of time slot objects"""
    def __init__(self, number, this_day):
        #old default time_slots = ['9:00-10:00', '11:00-13:00', '15:00-17:00']
        self.day = copy(this_day)
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
            logging.error("Invalid query for Room")
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
            this_schedule.append(TimeSlot(start.split(':'), end.split(':'), self))

        return this_schedule

    def __str__(self):
        return str(self.number) + "\n" + "\n".join([str(t) for t in self.schedule])

    def __iter__(self):
        for t_slot in self.schedule:
            yield t_slot


class TimeSlot:
    """A particular time slot, consisting of a time range and a course object"""
    def __init__(self, start_time, end_time, this_room, course = None):
        try:
            #make sure we are given 4 integers for times
            start_time = list(map(int, start_time))
            end_time = list(map(int, end_time))
        except ValueError:
            logging.error("Time slot unavailable with times given")
            print("Time slot unavailable with times given")
            return

        self.room = copy(this_room)
        self.start_time = time(start_time[0], start_time[1])
        self.end_time = time(end_time[0], end_time[1])
        self.course = course
        self.duration = self.find_duration(start_time, end_time)

    def info(self, query):
        """Goes up the object hierarchy to find object for given time slot
        Possible queries: Room, day, week, schedule
        IN: query string
        OUT: object of query's type for given time slot"""
        if query not in ["Room", "Day", "Week", "Schedule"]:
            logging.error("Invalid query for TimeSlot")
            print("Invalid query for TimeSlot")
            return
        elif query == "Room":
            return self.room
        elif query == "Day":
            return self.room.day
        elif query == "Week":
            return self.room.day.week
        elif query == "Schedule":
            return self.room.day.week.schedule

    def set_indices(self, day, room, slot):
        """Sets indices to refer to this object by cascading down"""
        self.day_index = day
        self.room_index = room
        self.slot_index = slot

    def find_duration(self, start_time, end_time):
        duration_hours = (end_time[0] - start_time[0]) * 60
        duration_min = end_time[1] - start_time[1]
        return duration_hours + duration_min
    
    def set_course(self, course):
        """Assigns a course to a time slot."""
        self.course = course

    def __str__(self):
        return "Course:%s\nStart time:%s\nEnd time:%s\nDuration:%s" % \
               (self.course, str(self.start_time), str(self.end_time),
                self.duration) +"\n"

    def __eq__(self, other):
        return self.start_time == other.start_time and \
               self.end_time == other.end_time


class Week:
    """A particular week of courses, consisting of 5 day objects"""
    def __init__(self, rooms, this_scheduler):
        """Initialize week object with list of room objects"""
        self.schedule = copy(this_scheduler)
        self.days = [Day(rooms, day_code, self) for day_code in 'mtwrf']
        self.fitness = 0

    def info(self, query):
        """Goes up the object hierarchy to find object for given week
        Possible queries: schedule
        IN: query string
        OUT: object of query's type for given week"""
        if query not in ["Schedule"]:
            logging.error("Invalid query for Week")
            print("Invalid query for Week")
            return
        elif query == "Schedule":
            return self.schedule

    def deep_copy(self):
        """Returns a deep copy of week"""
        return deepcopy(self)

    def find_time_slot(self, day, room, time_slot):
        """Returns the time slot for the given time
        IN: day, room, time objects
        OUT: corresponding time slot object"""
        for each_day in self.days:
            #todo: write __eq__ for all classes and change these comparisons accordingly
            if each_day.day_code == day.day_code:
                for each_room in each_day.rooms:
                    if each_room.number == room.number:
                        for each_time_slot in each_room.schedule:
                            if each_time_slot.start_time == time_slot.start_time:
                                return each_time_slot
        #todo: specificity on error; fail fast/gracefully
        logging.error("Time slot not found")
        print("Time slot not found")
        return

    def find_course(self, course):
        """Returns list of time slot objects for given course object in week
        IN: course object
        OUT: list of time slot objects"""
        time_slots = []
        for each_day in self.days:
            for each_room in each_day.rooms:
                for each_slot in each_room.schedule:
                    #If there is a course
                    if each_slot.course:
                        #If they are the same course
                        if each_slot.course.code == course.code:
                            time_slots.append(each_slot)
        if len(time_slots) > 0:
            return time_slots
        else:
            #todo: add specificity to logged error
            logging.error("Course not found")
            print("Course not found")
            return

    def __getitem__(self, k):
        if k not in "mtwrf":
            raise ValueError
        
        for day in self.days:
            if day.day_code == k:
                return day


    def __str__(self):
        """Returns string representation of given week"""
        return "\n".join([str(d) for d in self.days])


class Course:
    def __init__(self, code, credit):
        self.code = code
        self.credit = credit

    def __eq__(self, other):
        if other == None:
            return False

        return self.code == other.code and \
               self.credit == other.credit

    def __str__(self):
        return self.code

class Schedule:
    def __init__(self):
        pass
