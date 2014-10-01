from __future__ import print_function
import structures
from copy import copy
from copy import deepcopy


class Week:
    """A particular week of courses, consisting of 5 day objects"""
    def __init__(self, rooms, this_scheduler):
        """Initialize week object with list of room objects"""
        self.schedule = copy(this_scheduler)
        self.days = [structures.Day(rooms, day_code, self) for day_code in 'mtwrf']
        self.fitness = 0
        self.valid = True

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


