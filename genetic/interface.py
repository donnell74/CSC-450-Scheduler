import csv
from structures import *
import os
import yaml
import xml.etree.ElementTree as ET
from scheduler import *
from time import strftime, gmtime
from weakref import ref
from datetime import date, time as time_obj
import constraint

from Tkinter import Tk
from tkMessageBox import showinfo

def course_has_all_attributes(course):
    """
    Determine if a course object (built from yaml override, not a true Course object)
    has all requisite properties (code, period, credit, instructor,
                                  capacity, needs_computers, is_lab)
    IN: course object from yaml override
    OUT: True if course has all attributes else False
    """
    required_attributes = ["code", "period", "credit", "instructor", "capacity", "needs_computers", "is_lab"]
    for attribute in required_attributes:
        if attribute not in course:
            return False
    return True

def room_has_all_attributes(room):
    """
    Determine if a room object (built from yaml override, not a true Room object)
    has all requisite properties (building, number, capacity, has_computers)
    IN: room object from yaml override
    OUT: True if room has all attributes else False
    """
    required_attributes = ["building", "number", "capacity", "has_computers"]
    for attribute in required_attributes:
        if attribute not in room:
            return False
    return True

def get_semester_to_schedule(path_to_yaml):
    """
    Given the path to the override file, return the specific semester to be planned.
    If no valid override input is found, use today's date to guess at the semester
    and year. For example, if it is currently Fall or Winter, the guess will
    be for the Spring of the same year. If it is currently Spring or Summer,
    the guess will be for the Fall of next year.
    IN: path to yaml override file.
    OUT: a tuple representing the semester and year to be planned
        e.g.: ('Fall', 2015)
    """

    try:
        yaml_file = open(path_to_yaml, 'r')
        yaml_dict = yaml.load(yaml_file)
        yaml_file.close()

        semester_object = yaml_dict['data']['semester'].split(' ')
        fall_or_spring = semester_object[0].lower()
        if fall_or_spring in ['fall', 'fa', 'f']:
            fall_or_spring = "Fall"
        elif fall_or_spring in ['spring', 'sp', 's']:
            fall_or_spring = "Spring"
        else:
            raise IOError("Error: Invalid semester input.")

        # we know at least fall / spring
        if fall_or_spring == "Fall":
            year_upcoming = date.today().year
        else:
            year_upcoming = date.today().year + 1

        if len(semester_object) == 1: # no year is specified
            semester_year = year_upcoming
        elif int(semester_object[1]) < year_upcoming: # don't schedule past years
            semester_year = year_upcoming
        else:
            semester_year = int(semester_object[1])

        return (fall_or_spring, semester_year)

    except (IOError, TypeError): # override file not found or invalid information entered;
                                 # guess the semester to schedule
        # "day of year" ranges for the northern hemisphere
        spring_or_summer = range(80, 264)
        # fall_or_winter = everything else

        # get today's 'day number'. (Jan 1st -> 1)
        day_num = date.today().timetuple().tm_yday

        """
        If it is spring or summer, we guess that the semester to plan
        is the upcoming fall. Otherwise, we guess it is the upcoming spring.
        """
        if day_num in spring_or_summer:
            # we guess that we're planning for fall of the same year
            fall_or_spring = "Fall"
            semester_year = date.today().year
        else:
            # we guess that we're planning for spring of next year
            fall_or_spring = "Spring"
            semester_year = date.today().year + 1

        print "No override found. Guessing at the semester to be planned:",
        print fall_or_spring, semester_year
        return (fall_or_spring, semester_year)

    except ValueError:
        print "Invalid input. Please use the format 'Fall 2015'"
        return

    except Exception as e:
        print e
        return

## Function that Creates an xml input file (Input.xml) from yaml
#  @param path_to_global The path to the global input
#  @param path_to_override The path to the override input
#  @return none
def create_xml_input_from_yaml(path_to_global, path_to_override):
    """
    Creates an xml input file (Input.xml) from yaml.
    IN: path to yaml input
    OUT: None (does not return anything; creates Input.xml in genetic/seeds/)
    """
    def course_object_to_xml_string(code, period, credit, instructor, prereq,
                                    capacity, needs_computers, is_lab):
        # since "prereq='{}'".format('') -> "prereq=''''", we need an ugly conditional
        if prereq:
            unformatted_xml_string =  ("<item code='{0}' period='{1}' credit='{2}' instructor='{3}' prereq='{4}' "
                                       "capacity='{5}' needs_computers='{6}' is_lab='{7}'></item>")
            return unformatted_xml_string.format(code.upper(), period.upper(), credit, enforce_capital_first_letter(instructor),
                                                 prereq.upper(), capacity, needs_computers, is_lab)
        else: # prereq == None
            unformatted_xml_string =  ("<item code='{0}' period='{1}' credit='{2}' instructor='{3}' prereq='' "
                                       "capacity='{4}' needs_computers='{5}' is_lab='{6}'></item>")
            return unformatted_xml_string.format(code.upper(), period.upper(), credit, enforce_capital_first_letter(instructor),
                                                 capacity, needs_computers, is_lab)

    def room_object_to_xml_string(building, number, capacity, has_computers):
        unformatted_xml_string = ("<item building='{0}' number='{1}' capacity='{2}' "
                                  "has_computers='{3}'></item>")
        return unformatted_xml_string.format(building.upper(), number, capacity, has_computers)

    def print_number_spaces(num):
        return " " * num

    def print_indent(num):
        return print_number_spaces(2 * num)

    def schedule_tag(name):
        return "<schedule name='{0}'>".format(name)

    def tag(name, closing = False):
        if closing == True:
            return "</{0}>".format(name)
        else:
            return "<{0}>".format(name)

    def newline():
        return "\n"

    def xml_header():
        return "<?xml version='1.0'?>"

    def valid_credit_hour_input():
        ''' Validates that course credit hours are 1, 3, or 4.
            And that a lab is only 1 credit hour.
            Returns False if credit input is invalid.'''

        error_title = ''
        error_message = ''
        is_valid_input = True
        invalid_course_credits = False
        invalid_lab_credits = False

        # check for invalid credit hours
        for course in course_list:
            if not course['credit'] in [1, 3, 4] and course['is_lab'] == 0:
                if not invalid_course_credits:
                    invalid_course_credits = True
                else:
                    continue

                error_title = 'Error: course credit hours'
                error_message = 'Error for course {0}\n.'.format(course['code']) + \
                                'The course credit hour "' + str(course['credit']) + \
                                '" is \nnot an acceptable credit hour.' + \
                                '\nCredit hours must ' + \
                                'be 1, 3, or 4.\n' + \
                                '\nPlease change this in:\n' + \
                                'genetic\seeds\input.yaml'
                is_valid_input = False
                show_error_message(error_title, error_message)

            if course['is_lab'] == 1 and course['credit'] != 1:
                if not invalid_lab_credits:
                    invalid_lab_credits = True
                else:
                    continue

                error_title = 'Error: lab credit hours'
                error_message = 'Error for course {0}.\n'.format(course['code']) + \
                                'The lab credit hour "' + str(course['credit']) + \
                                '" is \nnot an acceptable lab credit.' + \
                                '\nLab credit must be 1 hour.\n' + \
                                '\nPlease change this in:\n' + \
                                'genetic\seeds\input.yaml'
                is_valid_input = False
                show_error_message(error_title, error_message)

        return is_valid_input

    def show_error_message(error_title, error_message):
        ''' Displays an error message '''

        root = Tk()
        root.withdraw() # hide tkinter window

        # display tkMessageBox
        showinfo(error_title, error_message)

    def this_course_in_course_list(course_code, course_list):
        for course in course_list:
            if course_code == course['code']:
                return True
        return False

    def update_attribute_in_course_list(course_code, attr, new_attr, course_list):
        try:
            for course in course_list:
                if course_code == course['code']:
                    course[attr] = str(new_attr)
        except:
            print "There was a problem with updating '" + str(attr) + "' for " + str(course_code)
        return course_list

    try:
        global_file = open(path_to_global, 'r')
        global_dict = yaml.load(global_file)
        global_file.close()

        yaml_data_object = global_dict['data']['schedule']
        schedule_name = yaml_data_object['name']
        course_list = yaml_data_object['course_list']
        time_list_tr = yaml_data_object['time_list_tr']
        time_list_mwf = yaml_data_object['time_list_mwf']
        room_list = yaml_data_object['room_list']

        if not valid_credit_hour_input():
            exit() # exit the scheduler

        override_file = open(path_to_override, 'r')
        override_dict = yaml.load(override_file)
        override_file.close()

        course_overrides = override_dict['data']['course_list']
        room_overrides = override_dict['data']['room_list']

        # if there are overrides, update the global vars before outputting
        if course_overrides:
            for this_course in course_overrides:
                # at least the course code must be specified
                if 'code' in this_course:
                    this_code = this_course['code']
                    if this_course_in_course_list(this_code, course_list):
                        # course already exists; modify information

                        if 'period' in this_course:
                            new_period = this_course['period']
                            course_list = update_attribute_in_course_list(this_code, "period",
                                                                          new_period, course_list)

                        if 'instructor' in this_course:
                            new_instructor = this_course['instructor']
                            course_list = update_attribute_in_course_list(this_code, "instructor",
                                                                          new_instructor, course_list)

                        if 'prereq' in this_course:
                            new_prereq = this_course['prereq']
                            course_list = update_attribute_in_course_list(this_code, "prereq",
                                                                          new_prereq, course_list)

                        if 'capacity' in this_course:
                            new_capacity = this_course['capacity']
                            course_list = update_attribute_in_course_list(this_code, "capacity",
                                                                          new_capacity, course_list)

                        if 'needs_computers' in this_course:
                            new_needs_computers = this_course['needs_computers']
                            course_list = update_attribute_in_course_list(this_code, "needs_computers",
                                                                          new_needs_computers, course_list)

                        if 'is_lab' in this_course:
                            new_is_lab = this_course['is_lab']
                            course_list = update_attribute_in_course_list(this_code, "is_lab",
                                                                          new_is_lab, course_list)

                    # course does not already exist; check for required information
                    elif course_has_all_attributes(this_course):
                        new_course = {'code':               this_course['code'].upper(),
                                      'period':             this_course['period'].upper(),
                                      'credit':             this_course['credit'],
                                      'instructor':         enforce_capital_first_letter(this_course['instructor']),
                                      'prereq':             this_course['prereq'].upper(),
                                      'capacity':           this_course['capacity'],
                                      'needs_computers':    this_course['needs_computers'],
                                      'is_lab':             this_course['is_lab']}
                        course_list.append(new_course)
                    else:
                        print "Incomplete information supplied in the override for " + \
                            this_course['code'] + ". Ignoring..."

        if room_overrides:
            for this_room in room_overrides:
                if room_has_all_attributes(this_room):
                    new_room = {"building": this_room['building'].upper(),
                                "number": this_room['number'],
                                "capacity": this_room['capacity'],
                                "has_computers": this_room['has_computers']}
                    room_list.append(new_room)

        # now that we have dealt with any existing overrides, output to xml
        xml_file = open('./genetic/seeds/Input.xml', 'w')
        indent_level = 0

        xml_file.write(print_indent(indent_level) + xml_header() + newline())
        xml_file.write(print_indent(indent_level) + tag("data") + newline())
        indent_level += 1

        xml_file.write(print_indent(indent_level) + schedule_tag(schedule_name) + newline())
        indent_level += 1

        xml_file.write(print_indent(indent_level) + tag("courseList") + newline())
        indent_level += 1

        for course in course_list:
            if course['prereq'] == None:
                course_prereq = ""
            else:
                course_prereq = course['prereq']
            course_xml_string = course_object_to_xml_string(code = course['code'],
                                                            period = course['period'],
                                                            credit = course['credit'],
                                                            instructor = course['instructor'],
                                                            prereq = course_prereq,
                                                            capacity = course['capacity'],
                                                            needs_computers = course['needs_computers'],
                                                            is_lab = course['is_lab'])
            xml_file.write(print_indent(indent_level) + course_xml_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("courseList", closing = True) + newline())
        xml_file.write(print_indent(indent_level) + tag("roomList") + newline())
        indent_level += 1

        for room in room_list:
            room_xml_string = room_object_to_xml_string(building = room['building'],
                                                        number = room['number'],
                                                        capacity = room['capacity'],
                                                        has_computers = room['has_computers'])
            xml_file.write(print_indent(indent_level) + room_xml_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("roomList", closing = True) + newline())
        xml_file.write(print_indent(indent_level) + tag("timeListMWF") + newline())
        indent_level += 1

        for time_slot in time_list_mwf:
            xml_time_slot_string = "{0}{1}{2}".format(tag("item"), time_slot, tag("item", closing = True))
            xml_file.write(print_indent(indent_level) + xml_time_slot_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("timeListMWF", closing = True) + newline())
        xml_file.write(print_indent(indent_level) + tag("timeListTR") + newline())
        indent_level += 1

        for time_slot in time_list_tr:
            xml_time_slot_string = "{0}{1}{2}".format(tag("item"), time_slot, tag("item", closing = True))
            xml_file.write(print_indent(indent_level) + xml_time_slot_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("timeListTR", closing = True) + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("schedule", closing = True) + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("data", closing = True) + newline())

        xml_file.close()

        return

    except Exception as exception_instance:
        print(exception_instance)
        return None


def enforce_capital_first_letter(str):
    """ ensures that a string takes the form "Abcd" instead of "abcd" or "ABCD" """
    first_letter = str[:1]
    rest_of_str = str[1:]
    first_letter = first_letter.upper()
    rest_of_str = rest_of_str.lower()
    fixed_str = first_letter + rest_of_str
    return fixed_str


def create_constraints_from_yaml(path_to_yaml, scheduler, instructor_objs):
    """ Takes an input YAML file (default_constraints.yaml) and generates appropriate
    constraints, then adds them to the scheduler.
    NOTE: Helper functions are defined first, and then the parsing and generating begins
    IN: a YAML file containing all the default constraints
    OUT: the constraints will be added to the program and displayed in the Added Constraints
    screen on the constraint page
    """

    def pull_instructor_obj(instructor_name):
        """ finds the instructor object for the given name """
        for instr in instructor_objs:
            if instructor_name.upper() == instr.name.upper():
                return instr

    def str_to_time(time_str):
        """ converts a time string ("12:30") into a time obj """
        t_hr, t_min = time_str.split(":")
        return time_obj( int(t_hr), int(t_min) )

    def get_priority_value(priority):
        """ Turns the string value of priority into the
        appropriate weight (int) value. """
        priority = enforce_capital_first_letter(priority)
        priorities = {"Low": 10,
                      "Medium": 25,
                      "High": 50
                      }
        # Look up number value from dict. Return 0 if mandatory
        priority = priorities.get(priority, 0)
        return priority


    def course_time(constraint_dict, scheduler):
        """ Takes a dictionary of data required for a course
        time constraint:  course_code, before_after, timeslot, priority.
        IN: a dictionary with appropriate data fields
        OUT: adds course constraint to scheduler.
        """
        constraint_dict["code"] = constraint_dict["code"].upper()
        constraint_name = constraint_dict["code"] + "_" +\
                            constraint_dict["before_after"].lower() + "_" \
                            + constraint_dict["time"]

        course_obj = constraint_dict["code"].upper()
        if course_obj == "All":
            course_obj = scheduler.courses
        else: # find the course object
            for c in scheduler.courses:
                if course_obj == c.code: # found it
                    course_obj = c
                    break

        # fail silently if invalid course
        try:
            if course_obj not in scheduler.courses:
                return
        except:
            return

        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False
        timeslot_obj = str_to_time(constraint_dict["time"])

        # scheduler.courses is course list
        if constraint_dict["before_after"].upper() == "BEFORE":
            scheduler.add_constraint(constraint_name,
                                        priority,
                                        constraint.course_before_time,
                                        [course_obj, timeslot_obj, is_mandatory])
        else: # after constraint
            scheduler.add_constraint(constraint_name,
                                        priority,
                                        constraint.course_after_time,
                                        [course_obj, timeslot_obj, is_mandatory])


    def course_day(constraint_dict, scheduler):
        """ Takes a dictionary of data required for a course
        day constraint:  code, day_code, priority.
        IN: a dictionary with appropriate data fields
        OUT: adds course constraint to scheduler.
        """
        constraint_name = constraint_dict["code"] + "_" + constraint_dict["day_code"].upper()

        course_obj = constraint_dict["code"]
        for c in scheduler.courses:
            if course_obj == c.code: # found it
                course_obj = c
                break

        # fail silently if invalid course
        try:
            if course_obj not in scheduler.courses:
                return
        except:
            return

        day_code = constraint_dict["day_code"].lower()

        if len(day_code) == 0 or len(day_code) == 5:
            return  # drop silently, bad constraint
        
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False
        
        scheduler.add_constraint(constraint_name,
                                    priority, 
                                    constraint.partial_schedule_day,
                                    [course_obj, day_code, is_mandatory])


    def course_room(constraint_dict, scheduler):
        """ Takes a dictionary of data required for a course
        room constraint:  code, rooms, priority.
        IN: a dictionary with appropriate data fields
        OUT: adds course constraint to scheduler.
        """
        rooms = constraint_dict["rooms"]
        for r in rooms:
            r = r.upper()
        
        constraint_name = constraint_dict["code"] + "_" + rooms[0].upper()
        if len(rooms) > 1:
            constraint_name += "..."

        course_obj = constraint_dict["code"]
        for c in scheduler.courses:
            if course_obj == c.code: # found it
                course_obj = c
                break

        # fail silently if invalid course
        try:
            if course_obj not in scheduler.courses:
                return
        except:
            return

        if len(rooms) == 0:
            return  # drop silently, bad constraint
        
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False
        
        scheduler.add_constraint(constraint_name,
                                    priority, 
                                    constraint.partial_schedule_room,
                                    [course_obj, rooms, is_mandatory])


    def avoid_overlap(constraint_dict, scheduler):
        """ Takes a dictionary of data required for a manual
        concurrence (avoid conflict) constraint:  code,
        start_time, end_time, courses, priority.
        IN: a dictionary with appropriate data fields
        OUT: adds course constraint to scheduler.
        """
        courses = constraint_dict["courses"]
        for i in range(len(courses)):
            courses[i] = courses[i].upper()
        
        constraint_name = "avoid overlap" + "_" + constraint_dict["code"].upper() + "_" + courses[0]
        if len(courses) > 1:
            constraint_name += "..."

        course_objs = []
        for each_course in courses:
            for c in scheduler.courses:
                if each_course.upper() == c.code.upper(): # found it
                    course_objs.append(c)
                    break

        # fail silently if invalid course
        try:
            for each_course_obj in course_objs:
                if each_course_obj not in scheduler.courses:
                    return
        except:
            return

        if len(courses) == 0:
            return  # drop silently, bad constraint

        day_code = constraint_dict["days"].lower()
        
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False

        start_time = str_to_time(constraint_dict["start_time"])
        end_time = str_to_time(constraint_dict["end_time"])
        
        scheduler.add_constraint(constraint_name,
                                    priority, 
                                    constraint.avoid_overlap,
                                    [course_objs, start_time,
                                    end_time, day_code, is_mandatory])


    def instructor_time_pref(constraint_dict, scheduler):
        """ This takes in a dictionary of the data required for an
        instructor time preference constraint.  instr_name, before_after, time, priority.
        IN:  A dictionary with the appropriate data fields
        OUT: adds the constraint to the scheduler
        """
        constraint_name = constraint_dict["instr_name"] + \
                            "_prefers_" + \
                            constraint_dict["before_after"].lower() + \
                            "_" + constraint_dict["time"]

        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False

        instr_obj = pull_instructor_obj(constraint_dict["instr_name"])
        if instr_obj is None: return # instructor does not exist; do not add constraint
        timeslot_obj = str_to_time(constraint_dict["time"])

        if constraint_dict["before_after"].lower() == "before":
            scheduler.add_constraint(constraint_name,
                                        priority,
                                        constraint.instructor_time_pref_before,
                                        [instr_obj, timeslot_obj, is_mandatory] )
        else: # after
            scheduler.add_constraint(constraint_name,
                                        priority,
                                        constraint.instructor_time_pref_after,
                                        [instr_obj, timeslot_obj, is_mandatory] )


    def max_courses(constraint_dict, scheduler):
        """ Takes a dictionary of required data to generate an
        instructor_max_courses constraint.
        IN:  a dictionary of appropriate data
        OUT: a max_courses constraint is added to the scheduler
        """
        constraint_dict["instr_name"] = enforce_capital_first_letter(constraint_dict["instr_name"])
        constraint_name = constraint_dict["instr_name"] + \
                            "_max_courses_" + str(constraint_dict["max_courses"])
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False

        max_courses = constraint_dict["max_courses"]
        instr_obj = pull_instructor_obj(constraint_dict["instr_name"])
        if instr_obj is None: return # instructor does not exist; do not add constraint
        scheduler.add_constraint(constraint_name,
                                    priority,
                                    constraint.instructor_max_courses,
                                    [instr_obj, max_courses, is_mandatory])


    def computer_pref(constraint_dict, scheduler):
        """ Takes a dictionary of required data to generate an
        instructor computer preference constraint.
        IN: a dictionary of appropriate data
        OUT: a computer_pref constraint added to the scheduler
        """
        constraint_dict["instr_name"] = enforce_capital_first_letter(constraint_dict["instr_name"])
        constraint_name = constraint_dict["instr_name"] + \
                            "_prefers_computers_" + \
                            enforce_capital_first_letter(str(constraint_dict["prefers_computers"]))
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False
        instr_obj = pull_instructor_obj(constraint_dict["instr_name"])

        if instr_obj is None: return # instructor does not exist; do not add constraint
        prefers_computers = bool(enforce_capital_first_letter(str(constraint_dict["prefers_computers"])))

        scheduler.add_constraint(constraint_name,
                                    priority,
                                    constraint.instructor_preference_computer,
                                    [instr_obj, prefers_computers, is_mandatory])


    def day_pref(constraint_dict, scheduler):
        """ Takes a dictionary of required data to generate an
        instructor day preference constraint.
        IN: a dictionary of appropriate data
        OUT: a day_pref constraint added to the scheduler
        """
        constraint_dict["instr_name"] = enforce_capital_first_letter(constraint_dict["instr_name"])
        constraint_name = constraint_dict["instr_name"] + \
                            "_prefers_" + constraint_dict["day_code"].upper()
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False
        instr_obj = pull_instructor_obj(constraint_dict["instr_name"])
        if instr_obj is None: return # instructor does not exist; do not add constraint
        day_code = constraint_dict["day_code"].lower()

        if len(day_code) == 0 or len(day_code) == 5:
            return  # drop silently, bad constraint

        scheduler.add_constraint(constraint_name,
                                    priority,
                                    constraint.instructor_preference_day,
                                    [instr_obj, day_code, is_mandatory])


    def instructor_break(constraint_dict, scheduler):
        """ Takes a dictionary of required data to generate an
        instructor break constraint.
        IN: a dictionary of appropriate data
        OUT: an instructor_break constraint added to the scheduler
        """
        constraint_dict["instr_name"] = enforce_capital_first_letter(constraint_dict["instr_name"])
        constraint_name = constraint_dict["instr_name"] + \
                            "_break_" + constraint_dict["break_start"] + \
                            "_" + constraint_dict["break_end"]
        priority = get_priority_value(constraint_dict["priority"])
        if priority == 0:
            is_mandatory = True
        else:
            is_mandatory = False
        instr_obj = pull_instructor_obj(constraint_dict["instr_name"])
        if instr_obj is None: return # instructor does not exist; do not add constraint
        gap_start = str_to_time(constraint_dict["break_start"])
        gap_end = str_to_time(constraint_dict["break_end"])

        scheduler.add_constraint(constraint_name,
                                    priority,
                                    constraint.instructor_break_constraint,
                                    [instr_obj, gap_start, gap_end, is_mandatory])

    # begin parsing YAML
    input_file = file(path_to_yaml, "r")
    yaml_dict = yaml.load(input_file)

    if yaml_dict["data"]["constraint_list"]["course_constraints"] is not None:
        # course constraints exist
        course_constraints = yaml_dict["data"]["constraint_list"]["course_constraints"]
        for type in course_constraints:
            if course_constraints[type] is not None:
                # course constraints exist
                for i in range(len(course_constraints[type])): # create each constraint of each type
                    this_constraint = course_constraints[type][i]
                    if type == "time":
                        course_time(this_constraint, scheduler)
                    elif type == "day":
                        course_day(this_constraint, scheduler)
                    elif type == "room":
                        course_room(this_constraint, scheduler)
                    elif type == "avoid_overlap":
                        avoid_overlap(this_constraint, scheduler)

    if yaml_dict["data"]["constraint_list"]["instructor_constraints"] is not None:
        instr_constraints = yaml_dict["data"]["constraint_list"]["instructor_constraints"]
        for type in instr_constraints:
            if instr_constraints[type] is not None:
                # instructor constraints exist
                for i in range(len(instr_constraints[type])): # create every constraint of each type
                    this_constraint = instr_constraints[type][i]
                    instr_constraints[type][i]["instr_name"] = enforce_capital_first_letter(instr_constraints[type][i]["instr_name"])
                    if type == "time_pref":
                        instructor_time_pref(this_constraint, scheduler)
                    elif type == "max_courses":
                        max_courses(this_constraint, scheduler)
                    elif type == "day_pref":
                        day_pref(this_constraint, scheduler)
                    elif type == "computer_pref":
                        computer_pref(this_constraint, scheduler)
                    elif type == "instructor_break":
                        instructor_break(this_constraint, scheduler)


## Function that reads an xml file and schedules all courses found in it
#  @param path_to_xml The path_to_xml parameter
#  @param slot_divide The slot_divide parameter
#  @return return_schedule
def create_scheduler_from_file_test(path_to_xml, slot_divide = 2):
    """Reads in an xml file and schedules all courses found in it
    IN: path to xml file as string
    OUT: scheduler object with one week based on the xml input"""
    tree = ET.parse(path_to_xml)
    root = tree.getroot()

    instructors = create_instructors_from_courses(path_to_xml)
    instructors_dict = dict(zip([inst.name for inst in instructors],
                           [inst for inst in instructors]))
    courses = create_course_list_from_file(path_to_xml, instructors_dict)
    rooms = create_room_list_from_file(path_to_xml)
    time_slots_mwf, time_slots_tr = create_time_slot_list_from_file(path_to_xml)
    time_slot_divide = slot_divide
    course_titles = [course.code for course in courses]
    setCourses = [i.attrib for i in root.findall("course")]
    return_schedule = Scheduler(courses, rooms, time_slots_mwf, time_slots_tr,
                                int(time_slot_divide))
    return_schedule.weeks.append( structures.Week(rooms, return_schedule) )
    return_schedule.weeks[0].fill_week(setCourses)
    return_schedule.weeks[0].update_sections(return_schedule.courses)
    return return_schedule


## Function that reads 5 xml file and creates week objects for these seeds
#  @param list_of_weeks_to_schedule_on The list_of_weeks_to_schedule_on parameter
#  @param path_to_seeds The path_to_seeds parameter
#  @return list_of_weeks_to_schedule_on
def create_weeks_from_seeds(list_of_weeks_to_schedule_on, path_to_seeds):
    """Reads 5 XML files and creates week objects for these seeds
    path_to_seeds should look like directory/seed
    Seed number and .xml will be appended to it"""
    counter = 0
    for each_week in list_of_weeks_to_schedule_on[:5]:
        counter += 1
        tree = ET.parse(path_to_seeds + str(counter) + '.xml')
        root = tree.getroot()
        setCourses = [i.attrib for i in root.findall("course")]
        each_week.fill_week(setCourses)
    return list_of_weeks_to_schedule_on


## Function that creates a list of course objects without an instructors_dict
#  @param path_to_xml The path_to_xml parameter
#  @return None
def create_course_list_from_file_test(path_to_xml):
    """For testing purposes.  Creates a list of course objects without an instructors_dict
    IN: path to xml file as string
    OUT: list of course objects based on xml"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructors = create_instructors_from_courses(path_to_xml)
        instructors_dict = dict(zip([inst.name for inst in instructors],
                                    [inst for inst in instructors]))
        courses = create_course_list_from_file(path_to_xml, instructors_dict)
        return courses
    except Exception as inst:
        print(inst)
        return None

def course_should_be_scheduled(period):
    """
    Determines if a course should be scheduled based on its periodicity.
    For example, if the semester being scheduled is Fall and a course is
    only taught in the Spring, it should be ignored.
    IN: periodicity of course being considered ["F", "B", "S", "D"]
    OUT: True if course should be scheduled else False
    """
    yaml_override_path = "genetic/seeds/override.yaml"
    this_semester = get_semester_to_schedule(yaml_override_path)[0]
    return (period in ["B"]) or \
            (this_semester == "Fall" and period == "F") or \
            (this_semester == "Spring" and period == "S")


## Function that reads an xml file and creates a list of course objects
#  @param path_to_xml The path_to_xml parameter
#  @param instructors_dict The instructors_dict parameter
#  @return List of course objects; courses are assigned to instructors
def create_course_list_from_file(path_to_xml, instructors_dict):
    """Reads an xml file and creates a list of course objects from it
    IN: xml path and an instructors_dict (instructor name, instructor object)
    OUT: list of course objects; courses are assigned to instructors"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructor_strings = [c.attrib["instructor"] for c in
                              root.find("schedule").find("courseList").getchildren()]
        courses = []
        for c in root.find("schedule").find("courseList").getchildren():
            instructor = instructors_dict[c.attrib["instructor"]]
            # only schedule courses with valid periodicity
            if c.attrib["period"] in ["F", "S", "B", "D"]:
                # only schedule courses with periodicity occuring in this semester
                if course_should_be_scheduled(c.attrib["period"]):
                    course = Course(code = c.attrib["code"],
                                    credit = int(c.attrib["credit"]),
                                    instructor = instructor,
                                    capacity = int(c.attrib["capacity"]),
                                    needs_computers = bool(int(c.attrib["needs_computers"])),
                                    is_lab = bool(int(c.attrib["is_lab"])))
                    instructor.add_course(course)
                    courses.append(course)
        return courses
    except Exception as inst:
        print(inst)
        return None


## Function that reads an xml file and creates a list of rooms objects
#  @param path_to_xml The path_to_xml parameter
#  @return List of rooms as strings
def create_room_list_from_file(path_to_xml):
    """Reads an xml file and creates a list of rooms (strings) from it
    IN: path to xml file
    OUT: list of rooms as strings"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        # rooms will be list of tuples
        rooms = []
        for r in root.find("schedule").find("roomList").getchildren():
            # Make tuple with (building, number, capacity, has_computers)
            room = (r.attrib["building"], r.attrib["number"], r.attrib["capacity"], r.attrib["has_computers"])
            rooms.append(room)
        return rooms
    except Exception as inst:
        print(inst)
        return None


## Function that reads an xml file and creates a list of time slots
#  @param path_to_xml The path_to_xml parameter
#  @return Tuple of 2 lists of time slots as strings (mwf and tr)
def create_time_slot_list_from_file(path_to_xml):
    """Reads an xml file and creates lists of time slots (strings) from it for mwf and tr
    IN: path to xml file
    OUT: tuple of 2 lists of time slots as strings (mwf and tr)"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        time_slots_mwf = [r.text for r in root.find("schedule").find("timeListMWF").getchildren()]
        time_slots_tr = [r.text for r in root.find("schedule").find("timeListTR").getchildren()]
        return (time_slots_mwf, time_slots_tr)
    except Exception as inst:
        print(inst)
        return None


## Function that reads an xml file and creates a dictionary of extras
#  @param path_to_xml The path_to_xml parameter
#  @return Dictionary of extras
def create_extras_list_from_file(path_to_xml):
    """Reads an xml file and creates a dictionary of extras
    IN: path to xml file
    OUT: dictionary of extras"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        extras = {}
        extras["input"] = dict([(parent.tag, [child.text for child in parent\
                    .getchildren()]) for parent in \
                    root.find("extra").find("input").getchildren()])
        extras["expected"] = dict([(parent.tag, [child.text for child in\
                    parent.getchildren()]) for parent in \
                    root.find("extra").getchildren()])["expected"]
        return extras
    except Exception as inst:
        print(inst)
        return None


## Function that reads an xml file and creates a list of unique instructor objects
#  @param path_to_xml The path_to_xml parameter
#  @return List of instructor objects
def create_instructors_from_courses(path_to_xml):
    """Reads an xml file and creates a list of unique instructor objects
    IN: path to xml file
    OUT: list of instructor objects"""
    instructors = []
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructors_unique = []
        instructors_raw = [course.attrib["instructor"] for course in
                           root.find("schedule").find("courseList").getchildren()]
        for each_instructor in instructors_raw:
            if each_instructor not in instructors_unique:
                instructors_unique.append(each_instructor)
        instructors_unique = map(lambda i: Instructor(i), instructors_unique)
        return instructors_unique
    except Exception as inst:
        print(inst)
        return None


# should be updated to final object attributes (pr)
def export_schedule_xml(week, extras="", prefix="", export_dir="./tests/schedules/"):
    """Exports given week as xml for testing purposes
    IN: week object, extras string, prefix string, export directory
    OUT: creates an xml file for the given input"""
    timestr = strftime("%Y%m%d-%H%M%S", gmtime())
    filename = os.path.join(export_dir, prefix + timestr + ".xml")
    with open(filename, 'w') as out:
        out.write("<?xml version='1.0'?>\n<data>\n")
        out.write("<schedule name='" + timestr + "'>\n")

        out.write("<courseList>\n")
        for each_course in week.schedule.courses:
            out.write("<item code='%s' credit='%d' instructor='%s' capacity='%d' needs_computers='%s'></item>\n"\
                  % (each_course.code, each_course.credit, each_course.instructor, \
                    each_course.capacity, each_course.needs_computers))

        out.write("</courseList>\n")

        out.write("<roomList>\n")
        for each_room in week.days[0].rooms:
            out.write("<item building='%s' number='%d' capacity='%d' has_computers='%s'\n" \
                    % (each_room.building, each_room.number, each_room.capacity, \
                        each_room.has_computers))

        out.write("</roomList>\n")

        out.write("<timeList>\n")
        for each_slot in week.schedule.time_slots:
            out.write("<item>%s</item>\n" % (each_slot))
        out.write("</timeList>\n")

        out.write("<timeSlotDivide>" + str(week.schedule.slot_divide) + "</timeSlotDivide>\n")
        out.write("</schedule>\n")

        # create the all the courses
        courses_dyct = {
        }  # structure of {course_code : (day_code, room, start_time, end_time)}
        instructors = []
        for each_slot in week.list_time_slots():
            if each_slot.course != None:
                if courses_dyct.has_key(each_slot.course.code):
                    courses_dyct[each_slot.course.code][3] += each_slot.day
                else:
                    courses_dyct[each_slot.course.code] = \
                        [each_slot.course.credit, \
                         each_slot.start_time, each_slot.end_time, \
                         each_slot.day, each_slot.room.building + " " + each_slot.room.number, \
                         each_slot.instructor]
                    if each_slot.instructor not in instructors:
                        instructors.append(each_slot.instructor)

        for instructor in instructors:
            for key in instructor.courses:
                # course / credit / startTime / endTime / room number / instructor
                out.write("""<course
code="%s"
credit="%s"
startTime="%s"
endTime="%s"
days="%s"
room="%s"
instructor="%s">
</course>\n""" % (str(key), str(courses_dyct[key.code][0]),\
                str(courses_dyct[key.code][1])[:-3], str(courses_dyct[key.code][2])[:-3], courses_dyct[key.code][3],\
                courses_dyct[key.code][4], courses_dyct[key.code][5]))

        out.write("<extra>\n%s</extra>\n" % (extras))
        out.write("</data>")



## Function that Exports top 5 valid schedules to csv f
#  @param weeks The weeks parameter
#  @param export_dir The export_dir parameter
#  @return Up to 5 csv files for top 5 valid schedules
def export_schedules(weeks, export_dir="./"):
    """Exports top 5 valid schedules to csv
    IN: list of week objects, export directory
    OUT: up to 5 csv files for top 5 valid schedules"""
    counter = 0
    num_to_export = len(weeks)
    for each_week in weeks:
        if each_week.valid:
            counter += 1
            if counter > 5:
                counter = 5
                break
            filename = os.path.join(export_dir, "schedule_" + str(counter) + ".csv")
            if os.path.isfile(filename):
                os.remove(filename)
            with open(filename, 'w') as out:
                out.write(each_week.print_concise().replace(' ', ','))
    print("\nExporting " + str(counter) + " schedules")

    counter += 1
    while counter <= 5:
        filename = os.path.join(
            export_dir, "schedule_" + str(counter) + ".csv")
        if os.path.isfile(filename):
            os.remove(filename)
        counter += 1


## Function that determine first-level prereqs from xml and list of all courses
#  @param path_to_xml The path_to_xml parameter
#  @param courses The courses parameter
#  @return List of prereq objects
def get_prereqs(path_to_xml, courses):
    """Determine first-level prereqs from xml and list of all courses
    IN: path to xml file, list of course objects
    OUT: list of prereq objects"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        list_of_prereqs = []
        for c in root.find("schedule").find("courseList").getchildren():
            #get strings
            prereq = c.attrib["prereq"]
            if not prereq: #if this course has no prereqs
                continue
            course_string = c.attrib["code"]
            #prepare for prereq operations
            prereq = prereq.split(' ')
            absolute_course = "".join(course_string.split(' ')[:2])
            #prereq operations
            prereq_obj = Prereq(absolute_course, courses)
            for each_prereq in prereq:
                prereq_obj.add_prereq(each_prereq, courses)
            list_of_prereqs.append(prereq_obj)
        return list_of_prereqs
    except Exception as inst:
        print(inst)
        return None


## Function that Extends prereqs for prereq of each prereq
#  @param prereqs The prereqs parameter
#  @param courses The courses parameter
#  @return list of prereq objects with extended prereqs accounted for
def get_extended_prereqs(prereqs, courses):
    """Extends prereqs for prereq of each prereq
    IN: list of prereq objects, list of all course objects
    OUT: list of prereq objects with extended prereqs accounted for"""
    def find_prereq(prereq_absolute_course, prereqs):
        for p in prereqs:
            if p.absolute_course == prereq_absolute_course:
                return p
        #if not found
        return None

    #courses with a prereq
    covered = [p.absolute_course for p in prereqs]
    for each_prereq in prereqs: #prereq object
        if len(each_prereq.absolute_prereqs) == 0:
            continue
        for each_absolute_prereq in covered:
            if each_absolute_prereq in each_prereq.absolute_prereqs:
                derived_prereq_obj = find_prereq(each_absolute_prereq, prereqs)
                derived_prereqs = derived_prereq_obj.absolute_prereqs
                #next(p for p in covered if each_absolute_prereq == p)
                for each_derived in derived_prereqs:
                    each_prereq.add_prereq(each_derived, courses)
    return prereqs
