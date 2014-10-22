from structures import *
from datetime import time, timedelta

def all_before_time(this_week, args):
    """ iterates through courses in the schedule to make sure
     none are before a specific time
     args should be [list of courses, timeslot]   
     Timeslot should be a time object:  time(12, 0) """

    hold = False

    for c in args[0]:  # access list of courses
        hold = course_before_time(this_week, [c, args[1]])
        if hold == False:
            return 0

    # if it made it through the loop, then there were no conflicts
    return 1


def all_after_time(this_week, args):
    """ iterates through courses in the schedule to make sure
     none are after a specific time
     args should be [list of courses, timeslot]   
     Timeslot should be a time object:  time(12, 0)
     """
    hold = False
    for c in args[0]:
        hold = course_after_time(this_week, [c, args[1]])
        if hold == False:
            return 0
    # if it made it through the loop, then there were no conflicts
    return 1


def course_before_time(this_week, args):
    # find the course and check that its time is before the constraining slot
    # args should be [<course>, <timeslot>]
    hold = this_week.find_course(args[0])[0].start_time < args[1]
    return 1 if hold else 0


def course_after_time(this_week, args):
    # find the course and check that its time is after the constraining slot
    # args should be [<course>, <timeslot>]
    hold = this_week.sectionfind_course(args[0])[0].start_time > args[1]
    return 1 if hold else 0


def morning_class(this_week, args):
    # Find course returns a list of time slots, but they should all be at the
    # same time
    holds = False
    if isinstance(args[0], Course):
        holds = this_week.find_course(args[0])[0].start_time < time(12, 0)

    return 1 if holds else 0


def instructor_time_pref_before(this_week, args):
	#args should be a list containing this_instructor, courses, and before_time;
	#this will have to be passed to you from the constraint generator
        #args looks like this [chosen_instructor, list_of_all_courses, chosen_before_or_after_time]
	this_instructor = args[0]
	time_slot = args[1]
	for each_course in this_instructor.courses:
		#section object for course
		each_section = this_week.find_section( each_course.code )
                if each_section.time_slots[0].start_time > time_slot:
                    #case 1: a course fails
                    return 0
	#case 2: all courses for instructor pass
	return 1


def instructor_time_pref_after(this_week, args):
	#args should be a list containing this_instructor, courses, and after_time;
	#this will have to be passed to you from the constraint generator
	this_instructor = args[0]
	time_slot = args[1]
	for each_course in this_instructor.courses:
		#section object for course
		each_section = this_week.find_section( each_course.code )
		#only want section obujects for this_instructor
                if each_section.time_slots[0].start_time < time_slot:
                        #case 1: a course fails
                        return 0
	#case 2: all courses for instructor pass
	return 1


def instructor_conflict(this_week, instructors):
    """
    Checks for instructors teaching multiple courses at once.  If none are found,
    passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    Todo: Check type of args
    IN: list of all instructor objects
    OUT: 0/1 for "holds"
    """
    for each_instructor in instructors:
        times = []
        count = 0
        for each_instructors_course in each_instructor.courses:
            times.append(
                this_week.find_course(each_instructors_course)[0].start_time)
        while len(times) > 0:
            each_time = times.pop(0)
            for each_other_time in times:
                if each_time == each_other_time:
                    count += 1
        if count > 0:
            this_week.valid = False
    return 0


def get_minutes(a_time):
    """
    return raw amount of minutes for the sake of comparison
    """
    return a_time.hour * 60 + a_time.minute


def times_are_sequential(timeslot1, timeslot2):
    """
    return true if timeslots are sequential, else false
    time_threshold can be used to give the max separation between timeslots
    """
    time_threshold = 0
    start2 = max(timeslot1.start_time, timeslot2.start_time)
    end1 = min(timeslot1.end_time, timeslot2.end_time)
    result = get_minutes(start2) - get_minutes(end1) - time_threshold <= 0
    return result


def sequential_time_different_building_conflict(this_week, instructors):
    """
    Checks if an instructor teaches a course in one bulding and in the following
    timeslot a different building. If this does not occur, passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    IN: list of all instructor objects
    OUT: 0/1 for "holds"
    """
    for instructor in instructors:
        instructor_slots = []
        count = 0
        for section in this_week.sections:
            if section.instructor == instructor:
                instructor_slots.append(section)
        for i in range(len(instructor_slots) - 1):
            section1 = instructor_slots[i]
            days1 = [day.day_code for day in section1.days]
            for j in range(i + 1, len(instructor_slots)):
                section2 = instructor_slots[j]
                days2 = [day.day_code for day in section2.days]
                if len(set(days1).intersection(days2)) > 0: #if sections days overlap
                    if times_are_sequential(section1.time_slots[0], section2.time_slots[0]):
                        if section1.room.building != section2.room.building:
                            count += 1
        if count > 0:
            this_week.valid = False
    return 0


def instructor_preference_day(this_week, args):
    instructor = args[0]
    day_code = args[1]
    
    for section_week in this_week.sections:
        if instructor.name == section_week.instructor.name:
            for day in section_week.days:
                if not day.day_code in day_code:
                    return 0
                    
    return 1


def num_subsequent_courses(this_week, instructors):
    TIME_BETWEEN_COURSES = 15  # can change this based on timeslot list
    for instructor in instructors:
        """ check each instructor's course list, then
        check each course's start time.  If there are
        3 courses with adjacent start times, fail entire constraint"""
        # WHEN WE IMPLEMENT MWF VS TR TIMES, THIS NEEDS TO BE EDITED FOR THAT
        course_list = instructor.courses
        for i in range(len(course_list)):
            course = course_list[i]
            c = this_week.find_course(course)[0]
            gap_time = time_finder(c.end_time, TIME_BETWEEN_COURSES)
            for j in range(i, len(course_list)):
                course_j = this_week.find_course(course_list[j])[0]
                if gap_time == course_j.start_time:
                    # check for third adjacent course
                    for k in range(j, len(course_list)):
                        k_gap_time = time_finder(course_j.end_time, TIME_BETWEEN_COURSES)
                        course_k = this_week.find_course(course_list[k])[0]
                        if k_gap_time == course_list[k].start_time: # third adjacent course
                            this_week.valid = False
                            return

    # if it didn't fail by now, it passed everyone
    return 0


def time_finder(end_t, time_gap):
    """ Helper function for num_subsequent_courses.
        Creates a new time object <time_gap> minutes after the end_t
        of a different course to mimic the next course's start time.
        Returns the new time object. """
    time_str = str(end_t)[:5]
    t_hr, t_min = time_str.split(":")
    t_hr = int(t_hr)
    t_min = int(t_min)
    if t_min < (59 - time_gap):  # can add the time_gap without problems
        t_min += time_gap
    else:  # less than time_gap to the next hour
        diff = 59 - time_gap
        t_hr += 1
        t_min = diff

    next_start_time = time(t_hr, t_min)
    return next_start_time


class Constraint:

    def __init__(self, name, weight, func, args=[]):
        if type(name) is not str:
            logging.error("Name is not a string")
            print("Name is not a string")
            return

        if type(weight) is not int:
            logging.error("Weight is not a string")
            print("Weight is not a string")
            return

        if not hasattr(func, '__call__'):
            if type(func) is str and not known_funcs.has_key(func):
                logging.error("Func string passed is not known")
                print("Func string passed is not known")
                return
            else:
                logging.error("Func passed is not a function")
                print("Func passed is not a function")
                return

        self.name = name
        self.weight = weight
        self.args = args
        if type(func) is str:
            self.func = func
        else:
            self.func = func

    def get_fitness(self, this_week):
        return self.func(this_week, self.args) * self.weight
