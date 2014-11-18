from __future__ import print_function
import structures
from copy import copy
from copy import deepcopy
from datetime import time
from weakref import ref

class MalformedWeekError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Week:

    """A particular week of courses, consisting of 5 day objects"""

    def __init__(self, rooms, this_scheduler, test = False):
        """Initialize week object with list of room objects"""
        if test:
            self.schedule = this_scheduler
        else:
            self.schedule = ref(this_scheduler)
        self.days = [structures.Day(rooms, day_code, self, test)
                     for day_code in 'mtwrf']
        self.fitness = 0
        self.valid = True
        self.num_invalid = 0
        self.complete = True
        #Week's copy of courses
        self.sections = []
        self.constraints = {}

    def info(self, query):
        """Goes up the object hierarchy to find object for given week
        Possible queries: schedule
        IN: query string
        OUT: object of query's type for given week"""
        if query not in ["Schedule"]:
            print("Invalid query for Week")
            return
        elif query == "Schedule":
            return self.schedule()

    def update_sections(self, courses):
        """Updates list of sections with all details
        IN: list of courses
        OUT: updated section attribute"""
        try:
            if len(self.sections) > 0:
                self.sections = []
            for each_course in courses:
                each_slots = self.find_course(each_course)
                each_section = structures.Section(each_course, each_slots)
                self.sections.append(each_section)
        except:
            print(each_course)
            print(self)

    def find_section(self, course_code):
        """IN: course_code as string
        OUT: section object; note that its attr's are shallow copies of structure objects
        Returns None if not found"""
        for each_section in self.sections:
            if each_section.course.code == course_code:
                #found
                return each_section
        #not found
        return None

    def deep_copy(self):
        """Returns a deep copy of week"""
        return deepcopy(self)


    def find_course(self, course):
        """Returns list of time slot objects for given course object in week
        IN: course object
        OUT: list of time slot objects"""
        time_slots = []
        for each_day in self.days:
            for each_room in each_day.rooms:
                for each_slot in each_room.schedule:
                    # If there is a course
                    if each_slot.course:
                        # If they are the same course
                        if each_slot.course.code == course.code:
                            time_slots.append(each_slot)
        return time_slots

    def __getitem__(self, k):
        if k not in "mtwrf":
            raise ValueError

        for day in self.days:
            if day.day_code == k:
                return day

    def list_time_slots(self):
        """Gives list of all time slot objects in week while indexing them"""
        list_of_slots = []
        # index counters
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


    def find_empty_time_slots(self):
        """Returns a list of empty (no course) time slot objects"""
        empty_slots = []
        for each_day in self.days:
            for each_room in each_day.rooms:
                for each_slot in each_room.schedule:
                    if each_slot.course is None:
                        empty_slots.append(each_slot)
        return empty_slots


    def is_empty(self):
        """Returns true is empty; else, false"""
        for each_day in self.days:
            for each_room in each_day.rooms:
                for each_slot in each_room.schedule:
                    if each_slot is not None:
                        return False
        return True


    def find_matching_time_slot_row(self, time_slot):
        """Returns the time slots in week that match in every time category except day
        This means same start time, end time, and room
        These time slots form a "row"
        IN: time slot object
        OUT: matching time slot objects from this week"""
        matching_time_slots = []
        for each_day in self.days:
            for each_room in each_day.rooms:
                if each_room.number == time_slot.room.number:
                    for each_time_slot in each_room.schedule:
                        if each_time_slot.start_time == time_slot.start_time and \
                           each_time_slot.end_time == time_slot.end_time:
                            matching_time_slots.append(each_time_slot)
        #todo: log error; this should only ever happen
        #if weeks are malformed
        if len(matching_time_slots) == 0:
            raise MalformedWeekError("Find Matching Time Slot Row")
        return matching_time_slots


    def find_matching_time_slot(self, time_slot):
        """Returns the single matching time slot in week
        This means same start time, end time, room, and day
        IN: time slot object
        OUT: matching time slot object from this week"""
        for each_day in self.days:
            if each_day.day_code == time_slot.room.day.day_code:
                for each_room in each_day.rooms:
                    if each_room.number == time_slot.room.number:
                        for each_time_slot in each_room.schedule:
                            if each_time_slot.start_time == time_slot.start_time and \
                               each_time_slot.end_time == time_slot.end_time:
                                return each_time_slot

        raise MalformedWeekError("Find Matching Time Slot")


    def fill_week(self, courses):
        """Fills the week based on the criteria listed in courses"""
        # check that courses has the correct structure
        #[{code:"CSC130", credit:"3", startTime:"11:00", endTime:"12:00", days:"MWF", room:"CHEK209"}, ...]

        try:
            # not using find_time_slot because this way should be faster
            for each_course in courses:
                start_hour, start_min = map(
                    int, each_course["startTime"].strip().split(':'))
                end_hour, end_min = map(
                    int, each_course["endTime"].strip().split(':'))
                startTime = time(start_hour, start_min)
                endTime = time(end_hour, end_min)
                # loop through days and find timeslot associated with
                # starttime, room, day
                for each_day in self.days:
                    if each_day.day_code in each_course["days"].lower():
                        for each_slot in each_day.get_room(each_course["room"].split()[1]):
                            if each_slot.start_time == startTime and \
                               each_slot.end_time == endTime:
                                for each_s_course in self.schedule().courses:
                                    if each_s_course.code == each_course["code"]:
                                        each_slot.course = each_s_course
                                        each_slot.instructor = each_s_course.instructor

        except KeyError, AttributeError:
            # error stuff
            print("Unable to fill week because bad input")

    def print_concise(self):
        """Returns a concise list of courses for week in the structure:
            course_code day_code room_number start_time-end_time"""
        try:
            courses_dyct = {
            }  # structure of {course_code : (day_code, room_number, start_time, end_time)}
            instructors = []
            for each_slot in self.list_time_slots():
                if each_slot.course != None:
                    if courses_dyct.has_key(each_slot.course.code):
                        courses_dyct[each_slot.course.code][0] += each_slot.day
                    else:
                        courses_dyct[each_slot.course.code] =  [each_slot.day, each_slot.room.building, \
                                                                each_slot.room.number, each_slot.start_time, \
                                                                each_slot.end_time, each_slot.instructor]
                        if each_slot.instructor not in instructors:
                            instructors.append(each_slot.instructor)

            concise_schedule_str = ""
            for instructor in instructors:
                concise_schedule_str += instructor.name + "\n"
                for key in instructor.courses:
                    # course / days / building / room number / start time / - / end time 
                    concise_schedule_str += str(key) + ' ' + courses_dyct[key.code][0] + ' ' + \
                        str(courses_dyct[key.code][1]) + ' ' + str(courses_dyct[key.code][2]) + ' ' + \
                        str(courses_dyct[key.code][3])[:-3] + '-' + str(courses_dyct[key.code][4])[:-3] + '\n'
                        #format start and end time to remove seconds value
        except:
            print(key)
            print(self)

        print ("=" * 25)
        print ("Fitness score: ", self.fitness)
        print ("Is Valid: ", self.valid)
        print (concise_schedule_str)
        [print(key, self.constraints[key]) for key in self.constraints.keys()]
        print ("=" * 25)
        return concise_schedule_str

    def __str__(self):
        """Returns string representation of given week"""
        return "\n".join([str(d) for d in self.days])
