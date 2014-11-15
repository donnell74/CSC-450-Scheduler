from structures import *
from datetime import time

def all_before_time(this_week, args):
    """Iterates through courses in the schedule to make sure
     none are before a specific time
     args should be [list of courses, timeslot, is_mandatory]
     Timeslot should be a time object:  time(12, 0) """

    list_of_course_objs = args[0]
    time_obj = args[1]
    is_mandatory = args[2]

    holds = []
    for course_obj in list_of_course_objs:  # access list of courses
        holds.append(course_before_time(this_week, [course_obj, time_obj]))

    if is_mandatory:
        if False in holds:
            this_week.valid = False
            return 0
        else:
            return 1
    else:  # not mandatory
        if False in holds:  # can be modified for partial credit?
            return 0
        else:  # no conflicts
            return 1


def all_after_time(this_week, args):
    """Iterates through courses in the schedule to make sure
     none are after a specific time
     args should be [list of courses, timeslot, is_mandatory]
     Timeslot should be a time object:  time(12, 0)
     """

    list_of_course_objs = args[0]
    time_obj = args[1]
    is_mandatory = args[2]

    holds = []

    for course_obj in list_of_course_objs:  # access list of courses
        holds.append(course_after_time(this_week, [course_obj, time_obj]))

    if is_mandatory:
        if False in holds:
            this_week.valid = False
            return 0
        else:
            return 1
    else:  # not mandatory
        if False in holds:
            return 0
        else:  # no conflicts
            return 1


def course_before_time(this_week, args):
    """find the course and check that its time is before the constraining slot
    args should be [<course>, <timeslot> [, is_mandatory] ]"""
    if len(args) > 2:  # includes the mandatory boolean
        is_mandatory = args[2]
    else:
        is_mandatory = False  # initialize it to false if not given

    hold = this_week.find_course(args[0])[0].start_time < args[1]

    if is_mandatory:
        if hold == 0:  # hold fails
            this_week.valid = False
            return 0
        else:
            return 1

    return 1 if hold else 0


def course_after_time(this_week, args):
    """find the course and check that its time is after the constraining slot
    args should be [<course>, <timeslot> [, is_mandatory] ]"""
    if len(args) > 2: #includes mandatory boolean
        is_mandatory = args[2]
    else:
        is_mandatory = False  # initialize it to false if not given

    hold = this_week.find_course(args[0])[0].start_time > args[1]

    if is_mandatory:
        if hold == 0:  # hold fails
            this_week.valid = False
            return 0
        else:
            return 1

    return 1 if hold else 0


def lab_on_tr(this_week, args):
    """ Checks that a lab course is scheduled on TR """
    return int(this_week.find_course(args[0])[0].isTR == True)


def morning_class(this_week, args):
    """Checks if the given course starts before 12
    args should be [<course>]"""
    holds = False
    if isinstance(args[0], Course):
        holds = this_week.find_course(args[0])[0].start_time < time(12, 0)

    return 1 if holds else 0


def instructor_time_pref_before(this_week, args):
    """ Checks if an instructor's courses are before a preferred time.
    args is [instructor_obj, time_obj, is_mandatory]
    Returns 0 or 1 if mandatory, else partial credit score.
    """
    instructor_obj = args[0]
    time_obj = args[1]
    is_mandatory = args[2]
    holds = [] # will contain 0's for all courses that fail constraint

    for course in instructor_obj.courses:
        #section object for course
        course_section = this_week.find_section(course.code)
        if course_section.time_slots[0].start_time > time_obj:
            #case 1: a course fails
            holds.append(0)
        else: # case 2: a course passes
            holds.append(1)

    if is_mandatory:
        if len(holds) >= 1: # at least one failure
            this_week.valid = False
            return 0
        else:
            return 1
    else: # not mandatory, treat it like normal
        if len(holds) >= 1:
            return 0
        else: # no failures, add the weight to the fitness score
            return 1


def instructor_time_pref_after(this_week, args):
    """ Checks if an instructor's courses are after a preferred time.
    args is [instructor_obj, time_obj, is_mandatory]
    Returns 1/0 if mandatory, else partial credit score.
    """
    instructor_obj = args[0]
    time_obj = args[1]
    is_mandatory = args[2]

    holds = [] # will contain 0's for all courses that fail constraint

    for course in instructor_obj.courses:
        #section object for course
        course_section = this_week.find_section(course.code)
        #only want section objects for this_instructor
        if course_section.time_slots[0].start_time < time_obj:
            #case 1: a course fails
            holds.append(0)
        else: # case 2: a course passes
            holds.append(1)

    if is_mandatory:
        if len(holds) >= 1: # at least one failure
            this_week.valid = False
            return 0
        else:
            return 1
    else: # not mandatory, treat it like normal
        if len(holds) >= 1:
            return 0
        else: # no failures, add the weight to the fitness score
            return 1


def instructor_conflict(this_week, args):
    """
    Checks for instructors teaching multiple courses at once.  If none
    are found, passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    IN: list of all instructor objects
    OUT: 0/1 if fail/pass, and sets week.valid accordingly
    """
    instructor_list = args[0]
    for instructor in instructor_list:
        times = []
        for instructors_course in instructor.courses:
            times.append(
                this_week.find_course(instructors_course)[0]
                )
        times.reverse()  # reverse so you don't have to pop(0)
        while len(times) > 0:
            first_time = times.pop()
            for i in range(len(times)):
                if is_overlap(first_time, times[i]):
                    this_week.valid = False
                    return 0
    return 1


def get_minutes(a_time):
    """
    return raw amount of minutes from a time object for comparison
    """
    return a_time.hour * 60 + a_time.minute


def times_are_sequential(timeslot1, timeslot2, time_threshold = 15):
    """
    return true if timeslots are sequential, else false
    time_threshold can be used to give the max separation between timeslots
    """
    later_start_time = max(timeslot1.start_time, timeslot2.start_time)
    earlier_end_time = min(timeslot1.end_time, timeslot2.end_time)
    result = get_minutes(later_start_time) - get_minutes(earlier_end_time)
    result = (result - time_threshold) <= 0
    return result


def sequential_time_different_building_conflict(this_week, args):
    """
    Checks if an instructor teaches a course in one building and in the next
    timeslot a different building. If this does not occur, passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    IN: list of all instructor objects
    OUT: 0/1 for "holds"
    """
    instructor_objs = args[0]
    for instructor in instructor_objs:
        instructor_slots = []

        for section in this_week.sections:
            if section.instructor == instructor:
                instructor_slots.append(section)
        for i in range(len(instructor_slots) - 1): #each section
            section1 = instructor_slots[i]
            days1 = [day.day_code for day in section1.days]
            for j in range(i + 1, len(instructor_slots)): #each other section
                section2 = instructor_slots[j]
                days2 = [day.day_code for day in section2.days]
                if len(set(days1).intersection(days2)) > 0: #if sections' days overlap
                    if times_are_sequential(section1.time_slots[0], section2.time_slots[0]):
                        if section1.room.building != section2.room.building:
                            this_week.valid = False
                            return 0
    return 1


def instructor_preference_day(this_week, args):
    """Check if instructor's day preference holds or not
    Args should be [instructor, list_of_day_codes, is_mandatory]"""
    instructor = args[0]
    day_code = args[1]
    is_mandatory = args[2]

    for section_week in this_week.sections:
        if instructor.name == section_week.instructor.name:
            for day in section_week.days:
                if not day.day_code in day_code:
                    if is_mandatory:
                        this_week.valid = False
                    return 0

    return 1

def instructor_preference_computer(this_week, args):
    """If an instructor prefers to teach in a class with
    or without computers, validate the week on this criteria.
    Args should be [instructor, computer_preference, is_mandatory]"""
    instructor = args[0]
    computer_preference = args[1]
    is_mandatory = args[2]

    for section_week in this_week.sections:
        if section_week.instructor.name == instructor.name:
            if computer_preference == True:
                #instructor prefers computers
                if section_week.room.has_computers == False:
                    if is_mandatory:
                        this_week.valid = False
                    return 0
            else:
                #instructor doesn't prefer computers
                if section_week.room.has_computers == True:
                    if is_mandatory:
                        this_week.valid = False
                    return 0
    #passes
    return 1


def is_overlap(timeslot1, timeslot2):
    """Return true if timeslots overlap else false"""
    if timeslot1.start_time < timeslot2.start_time:
        start_1st, start_2nd = timeslot1, timeslot2
    else:
        start_1st, start_2nd = timeslot2, timeslot1

    if start_2nd.start_time < start_1st.end_time:
        return True

    if start_1st.start_time == start_2nd.start_time:
        return True

    return False

def no_overlapping_courses(this_week, args):
    """Check that all timeslots do not overlap any other
    timeslots.  Args is an empty list because there is
    nothing to pass except for the week object."""
    times = []
    all_time_slots = this_week.list_time_slots()
    for each_timeslot in all_time_slots:
        if each_timeslot.course != None:
            times.append(each_timeslot)

    times.reverse()  # reverse so you don't pop(0)
    while len(times) > 0:
        first_time = times.pop()
        for i in range(len(times)):
            if first_time.day != times[i].day or \
               first_time.room != times[i].room:
                continue
            if is_overlap(first_time, times[i]):
                this_week.valid = False
                return 0

    return 1


def num_subsequent_courses(this_week, args):
    """An instructor may not have more than 2 courses back-to-back
    Args should be [list_of_instructors]"""

    instructors = args[0]

    for instructor in instructors:
        instructor_slots = []
        for section in this_week.sections:
            if section.instructor == instructor:
                instructor_slots.append(section)

        for i in range(len(instructor_slots) - 2): #first in combination
            section1 = instructor_slots[i]
            days1 = [day.day_code for day in section1.days]
            for j in range(i + 1, len(instructor_slots) - 1): #second in combination
                section2 = instructor_slots[j]
                days2 = [day.day_code for day in section2.days]
                for k in range(j + 1, len(instructor_slots)): #third in combination
                    section3 = instructor_slots[k]
                    days3 = [day.day_code for day in section3.days]
                    all_days = [days1, days2, days3]

                    if len(set(all_days[0]).intersection(*all_days[1:])) > 0:
                        #sections day overlap
                        compare_1_2 = times_are_sequential(
                            section1.time_slots[0],
                            section2.time_slots[0]
                            )
                        compare_2_3 = times_are_sequential(
                            section2.time_slots[0],
                            section3.time_slots[0]
                            )
                        compare_1_3 = times_are_sequential(
                            section1.time_slots[0],
                            section3.time_slots[0]
                            )

                        if (compare_1_2 and compare_2_3) or \
                           (compare_1_3 and compare_2_3) or \
                           (compare_1_3 and compare_1_2): #if have 3 subsequent courses
                            this_week.valid = False
                            return 0
    return 1


def ensure_course_room_capacity(this_week, args):
    """A course must be assigned to a room with enough capacity to
    hold the course's capacity.
    Args is an empty list; all relevant data is in this_week.
    """

    for section in this_week.sections:
        if section.course.capacity > section.room.capacity:
            this_week.valid = False
            return 0

    return 1


def ensure_computer_requirement(this_week, args):
    """ If a course is specified as requiring computers, its assigned
    room must also have computers to make its week valid.
    Args is an empty list; all relevant data is in this_week.
    """

    for section in this_week.sections:
        if section.course.needs_computers == True:
            if section.room.has_computers == False:
                this_week.valid = False
                return 0

    return 1


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


class ConstraintCreationError(Exception):
    """ Defines an error that occurs while creating a constraint."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConstraintCalcFitnessError(Exception):
    """ Defines an error that occurs while calcuting constraint fitness."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


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
        course_i_code = course_list[i].code.split(' ')  # ['csc', '130', '001']
        course_i_base_code = course_i_code[0] + course_i_code[1] # 'csc130'
        for j in range(i + 1, len(course_list)):
            course_j_code = course_list[j].code.split(' ')
            course_j_base_code = course_j_code[0] + course_j_code[1]
            if course_i_base_code == course_j_base_code:
                # same base course, different sections, so pull time slots
                course_i_time = this_week.find_course(course_list[i])[0].start_time
                course_j_time = this_week.find_course(course_list[j])[0].start_time
                if course_i_time == course_j_time:
                    # check the day codes to be sure it's not MWF at 9 and TR at 9
                    course_i_days = this_week.find_section(course_list[i].code).days
                    course_j_days = this_week.find_section(course_list[j].code).days
                    # now make intersection of lists
                    days_in_common = list(set(course_i_days) & set(course_j_days))

                    if len(days_in_common) > 0:  # at least one day in common
                        this_week.valid = False
                        return 0

    # no same course/different section at the same time; week is valid
    return 0

class Constraint:
    """ Defines a constraint for the scheduler.  It includes the
    constraint name (unique), a weight, the constraint function,
    and a list of relevant arguments.  """
    def __init__(self, name, weight, func, args=[]):
        if type(name) is not str:
            raise ConstraintCreationError("Name is not a string")

        if type(weight) is not int:
            raise ConstraintCreationError("Weight is not a string")

        if not hasattr(func, '__call__'):
            raise ConstraintCreationError("Func passed is not a function")

        self.name = name
        self.weight = weight
        self.args = args
        self.func = func

    def get_fitness(self, this_week):
        #fitness score
        if self.weight != 0:
            return self.func(this_week, self.args) * self.weight
        #is_valid (from this constraint)
        else:
            return self.func(this_week, self.args) * 1

