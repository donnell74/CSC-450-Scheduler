from __future__ import print_function
from datetime import time, timedelta
import logging
import random

class Day:
    def __init__(self, rooms, day_code):
        self.rooms = [Room(number) for number in rooms]
        if day_code.lower() in 'mtwrf':
            self.day_code = day_code
        else:
            logging.error("Day code was not recognized")
            print("Day code was not recognized")
            return

    def __str__(self):
        return "-----------------------\n" + \
                "Day: " + self.day_code + '\n' + "Rooms:\n" + \
                "\n".join([str(r) for r in self.rooms])

class Room:
    def __init__(self, number, time_slots = ['9:00-10:00', '11:00-13:00', '15:00-17:00']):
        self.number = number
        self.schedule = self.generate_time_slots(time_slots)

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
    def __init__(self, start_time, end_time, this_room, course = None):
        try:
            #make sure we are given 4 integers for times
            start_time = list(map(int, start_time))
            end_time = list(map(int, end_time))
        except ValueError:
            logging.error("Time slot unavailable with times given")
            print("Time slot unavailable with times given")
            return

        self.start_time = time(start_time[0], start_time[1])
        self.end_time = time(end_time[0], end_time[1])
        self.course = course
        self.duration = self.find_duration(start_time, end_time)
        self.room = this_room

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
    """A particular week of courses"""
    def __init__(self, rooms):
        self.days = [Day(rooms, day_code) for day_code in 'mtwrf']
        self.fitness = 0

    def find_time_slot(self, day, time):
        """Returns a time slot for the given time
        IN: day represented as one character, time (xx:xx), week object
        OUT: corresponding time slot object"""
        for each_day in self.days:
            if each_day.day_code == time.lower():
                for each_room in each_day.rooms:
                    for each_time_slot in each_room.schedule:
                        if each_time_slot.start_time == time:
                            return each_time_slot
        #todo: specificity
        logging.error("Time slot not found")

    def assign_course(self, course, time_slot):
        """Doc"""
        pass

    def __str__(self):
        return "\n".join([str(d) for d in self.days])

    def find_course(self, course):
        for each_day in self.days:
            for each_room in each_day.rooms:
                for each_slot in each_room.schedule:
                    if each_slot.course == course:
                        return each_slot
        #todo: add specificity to logged error
        logging.error("Course not found")
        return

    def __getitem__(self, k):
        if k not in "mtwrf":
            raise ValueError
        
        for day in self.days:
            if day.day_code == k:
                return day



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

#Todo: decide on week/schedule
class Schedule:
    def __init__(self):
        pass
