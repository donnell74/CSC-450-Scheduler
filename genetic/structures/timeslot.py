from __future__ import print_function
import structures
from copy import copy
from datetime import time, timedelta

class TimeSlot:
    """A particular time slot, consisting of a time range and a course object"""
    def __init__(self, start_time, end_time, this_room, course = None):
        try:
            #make sure we are given 4 integers for times
            start_time = list(map(int, start_time))
            end_time = list(map(int, end_time))
        except ValueError:
            print("Time slot unavailable with times given")
            return

        self.room = copy(this_room)
        self.day = self.room.day.day_code
        self.start_time = time(start_time[0], start_time[1])
        self.end_time = time(end_time[0], end_time[1])
        self.course = course
        self.duration = self.find_duration(start_time, end_time)
        self.instructor = None

    def info(self, query):
        """Goes up the object hierarchy to find object for given time slot
        Possible queries: Room, day, week, schedule
        IN: query string
        OUT: object of query's type for given time slot"""
        if query not in ["Room", "Day", "Week", "Schedule"]:
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
        if course is not None:
            self.instructor = course.instructor

    def remove_course(self):
        """Removes course and instructor associations from time slot"""
        self.course = None
        self.instructor = None

    def __str__(self):
        return "Course:%s\nInstructor:%s\nStart time:%s\nEnd time:%s\nDuration:%s" % \
               (self.course, str(self.instructor), str(self.start_time), str(self.end_time),
                self.duration) +"\n"

    def __eq__(self, other):
        return self.start_time == other.start_time and \
               self.room == other.room and \
               self.day == other.day


