from __future__ import print_function
import structures
from copy import copy
from copy import deepcopy
from datetime import time


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

    def list_time_slots(self):
        """Gives list of all time slot objects in week while indexing them"""
        list_of_slots = []
        #index counters
        day = 0
        room = 0
        slot = 0
        
        for each_day in self.days:
            for each_room in each_day.rooms:
                for each_slot in each_room.schedule:
                    list_of_slots.append(each_slot)
                    each_slot.set_indices(day, room, slot)
                    slot += 1
                room += 1
                slot = 0
            day += 1
            room = 0
        return list_of_slots


    def fill_week(self, courses):
        """Fills the week based on the criteria listed in courses"""
        #check that courses has the correct structure
        #[{code:"CSC130", credit:"3", startTime:"11:00", endTime:"12:00", days:"MWF", room:"CHEK209"}, ...]

        try:
            #not using find_time_slot because this way should be faster 
            print(courses)
            print('=' * 30)
            print(self.days)
            for each_course in courses:
                start_hour, start_min = map(int, each_course["startTime"].strip().split(':'))
                end_hour, end_min = map(int, each_course["endTime"].strip().split(':'))
                startTime = time(start_hour, start_min)
                endTime = time(end_hour, end_min)
                #loop through days and find timeslot associated with starttime, room, day
                for each_day in self.days:
                    if each_day.day_code in each_course["days"].lower():
                        print("day")
                        for each_slot in each_day.get_room(each_course["room"]):
                            if each_slot.start_time == startTime and \
                               each_slot.end_time == endTime:
                                print("time")
                                for each_s_course in self.schedule.courses:
                                    if each_s_course.code == each_course["code"]: 
                                        print("course")
                                        each_slot.course = each_s_course 


        except KeyError, AttributeError:
            #error stuff
            print("Unable to fill week because bad input")


    def print_concise(self):
        """Returns a concise list of courses for week in the structure:
            course_code day_code room_number start_time-end_time"""
        courses_dyct = {} # structure of {course_code : (day_code, room_number, start_time, end_time)}
        for each_slot in self.list_time_slots():
            if each_slot.course != None:
                if courses_dyct.has_key(each_slot.course.code):
                    courses_dyct[each_slot.course.code][0] += each_slot.day
                else:
                    courses_dyct[each_slot.course.code] = [each_slot.day, each_slot.room.number, \
                                                           each_slot.start_time, each_slot.end_time]
        concise_schedule_str = ""
        for key, value in courses_dyct.items():
            concise_schedule_str += str(key) + ' ' + value[0] + ' ' + str(value[1]) + ' ' + str(value[2]) + '-' + str(value[3]) + '\n' 

        return concise_schedule_str

    def __str__(self):
        """Returns string representation of given week"""
        return "\n".join([str(d) for d in self.days])
