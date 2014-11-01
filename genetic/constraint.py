from structures import *
from datetime import time, timedelta
#import sys
#sys.path.append("../")
#import globs

def all_before_time(this_week, args):
    """ iterates through courses in the schedule to make sure
     none are before a specific time
     args should be [list of courses, timeslot, is_mandatory]   
     Timeslot should be a time object:  time(12, 0) """

    holds = []
    is_mandatory = args[2]

    for c in args[0]:  # access list of courses, don't pass is_mandatory 
        holds.append(course_before_time(this_week, [c, args[1]]))

    if is_mandatory:
        if False in holds:
            this_week.valid = False
            return 0
        else:
            this_week.valid = True
            return 0 
    else:  # not mandatory
        if False in holds:  # can be modified for partial credit?
            return 0
        else:  # no conflicts
            return 1  
    

def all_after_time(this_week, args):
    """ iterates through courses in the schedule to make sure
     none are after a specific time
     args should be [list of courses, timeslot]   
     Timeslot should be a time object:  time(12, 0)
     """
    holds = []
    is_mandatory = args[2]

    for c in args[0]:  # access list of courses, don't pass is_mandatory 
        holds.append(course_after_time(this_week, [c, args[1]]))

    if is_mandatory:
        if False in holds:
            this_week.valid = False
            return 0
        else:
            this_week.valid = True
            return 0 
    else:  # not mandatory
        if False in holds:  # can be modified for partial credit?
            return 0
        else:  # no conflicts
            return 1  


def course_before_time(this_week, args):
    # find the course and check that its time is before the constraining slot
    # args should be [<course>, <timeslot> [, is_mandatory] ]
    if len(args) > 2:  # includes the mandatory boolean
        is_mandatory = args[2]
    
    hold = this_week.find_course(args[0])[0].start_time < args[1]

    if is_mandatory:
        if hold == 0:  # hold fails
            this_week.valid = False
            return 0
        else:
            this_week.valid = True
            return 0

    return 1 if hold else 0


def course_after_time(this_week, args):
    # find the course and check that its time is after the constraining slot
    # args should be [<course>, <timeslot> [, is_mandatory] ]
    if len(args) > 2: #includes mandatory boolean
        is_mandatory = args[2]
        
    hold = this_week.find_course(args[0])[0].start_time > args[1]

    if is_mandatory:
        if hold == 0:  # hold fails
            this_week.valid = False
            return 0
        else:
            this_week.valid = True
            return 0
    
    return 1 if hold else 0


def morning_class(this_week, args):
    # Find course returns a list of time slots, but they should all be at the
    # same time
    holds = False
    if isinstance(args[0], Course):
        holds = this_week.find_course(args[0])[0].start_time < time(12, 0)

    return 1 if holds else 0


def instructor_time_pref_before(this_week, args):
    #args should be a list containing this_instructor, courses, and
        # before_time;
    #this will have to be passed to you from the constraint generator
        #args looks like this [chosen_instructor, timeslot, is_mandatory]
    this_instructor = args[0]
    time_slot = args[1]
    is_mandatory = args[2]
    holds = [] # will contain 0's for all courses that fail constraint

    for each_course in this_instructor.courses:
        #section object for course
        each_section = this_week.find_section( each_course.code )
        if each_section.time_slots[0].start_time > time_slot:
                    #case 1: a course fails
                    holds.append(0)
                    
        if is_mandatory:
            if len(holds) >= 1: # at least one failure
                this_week.valid = False
                return 0
            else:
                this_week.valid = True
                return 0
        else: # not mandatory, treat it like normal
            if len(holds) >= 1:
                   return 0
            else: # no failures, add the weight to the fitness score
                   return 1


def instructor_time_pref_after(this_week, args):
    #args should be a list containing this_instructor, courses,
        # and after_time
    #this will have to be passed to you from the constraint generator
    this_instructor = args[0]
    time_slot = args[1]
    is_mandatory = args[2]
    print(this_week.schedule.instructors[0])
    holds = [] # will contain 0's for all courses that fail constraint
    
    for each_course in this_instructor.courses:
        #section object for course
        each_section = this_week.find_section( each_course.code )
        #only want section obujects for this_instructor
        if each_section.time_slots[0].start_time < time_slot:
            #case 1: a course fails
            holds.append(0)
                   
        if is_mandatory:
            if len(holds) >= 1: # at least one failure
                this_week.valid = False
                return 0
            else:
                this_week.valid = True
                return 0
        else: # not mandatory, treat it like normal
            if len(holds) >= 1:
                   return 0
            else: # no failures, add the weight to the fitness score
                   return 1


def instructor_conflict(this_week, args):
    """
    Checks for instructors teaching multiple courses at once.  If none are found,
    passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    Todo: Check type of args
    IN: list of all instructor objects
    OUT: 0/1 for "holds"
    """
    instructors = args[0]
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


def sequential_time_different_building_conflict(this_week, args):
    """
    Checks if an instructor teaches a course in one bulding and in the following
    timeslot a different building. If this does not occur, passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    IN: list of all instructor objects
    OUT: 0/1 for "holds"
    """
    instructors = args[0]
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


def num_subsequent_courses(this_week, args):
    """An instructor may not have more than 2 courses back-to-back"""
    instructors = args[0]
    for instructor in instructors:
        instructor_slots = []
        count = 0
        for section in this_week.sections:
            if section.instructor == instructor:
                instructor_slots.append(section)
        for i in range(len(instructor_slots) - 2):
            section1 = instructor_slots[i]
            days1 = [day.day_code for day in section1.days]
            for j in range(i + 1, len(instructor_slots) - 1):
                section2 = instructor_slots[j]
                days2 = [day.day_code for day in section2.days]
                for k in range(j + 1, len(instructor_slots)):
                    section3 = instructor_slots[k]
                    days3 = [day.day_code for day in section3.days]
                    all_days = [days1, days2, days3]
                    if len(set(all_days[0]).intersection(*all_days[1:])) > 0: #if sections days overlap
                        compare_1_2 = times_are_sequential(section1.time_slots[0], section2.time_slots[0])
                        compare_2_3 = times_are_sequential(section2.time_slots[0], section3.time_slots[0])
                        compare_1_3 = times_are_sequential(section1.time_slots[0], section3.time_slots[0])
                        if (compare_1_2 and compare_2_3) or (compare_1_3 and compare_2_3) or \
                           (compare_1_3 and compare_1_2):
                            count += 1
        if count > 0:
            this_week.valid = False
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


def course_sections_at_different_times(this_week, arg):
	""" Ensures that different sections of a course with the same absolute name
	such as CSC 130 001 or 002, are not scheduled at the same time.
	NOTE: this should work for both section numbers and lab sections denoted by
	letters.
	IN: the list of all courses 
	OUT: Returns 0 and adjusts week.valid as necessary
	"""
        course_list = arg[0]
	for i in range(len(course_list)):
		i_code = course_list[i].code.split(' ')  # ['csc', '130', '001']
		course_i_base_code = i_code[0] + i_code[1] # 'csc130'
		for j in range(i + 1, len(course_list)):
			j_code = course_list[j].code.split(' ')
			course_j_base_code = j_code[0] + j_code[1]
			if course_i_base_code == course_j_base_code:  
				# same base course, different sections, so pull time slots
				course_i_time = this_week.find_course(course_list[i])[0].start_time
				course_j_time = this_week.find_course(course_list[j])[0].start_time
				if course_i_time == course_j_time:
					# check the day codes to be sure it's not MWF at 9 and TR at 9
					course_i_days = this_week.find_section(course_list[i].code).days
					course_j_days = this_week.find_section(course_list[j].code).days
					days_in_common = list(set(course_i_days) & set(course_j_days)) # intersection of lists
					if len(days_in_common) > 0:  # at least one day in common
						this_week.valid = False
						return 0
	
	# no same course/different section at the same time - week is valid
	return 0

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
