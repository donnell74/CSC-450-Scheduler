from Tkinter import Frame, Label, StringVar, OptionMenu, Button
from Tkconstants import TOP, RIGHT
from datetime import time
import globs
from genetic import constraint
import tkMessageBox

class CourseConstraint(Frame):
    """Course constraint frame"""

    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        globs.init()

        self.constraints_view_obj = constraints_view_obj

        message_course = Label(self, text="Course code:")
        message_course.pack(side = TOP)

        self.str_course_default = StringVar(self)
        list_of_courses = globs.courses
        list_of_courses.append("All")
        self.str_course_default.set(list_of_courses[0])
        self.option_course = OptionMenu(self, self.str_course_default, *list_of_courses)
        self.option_course.pack(side = TOP)

        message_when = Label(self, text="When:")
        message_when.pack(side = TOP)

        self.str_when_default = StringVar(self)
        self.str_when_default.set("Before")
        self.str_when_default.trace("w", self.callback_after_before)
        self.option_when = OptionMenu(self, self.str_when_default, "Before", "After")
        self.option_when.pack(side = TOP)

        message_time = Label(self, text="Time:")
        message_time.pack(side = TOP)

        self.str_time_default = StringVar(self)
        self.str_time_default.set(globs.start_times[1]) #set the second element
        self.option_time = OptionMenu(self, self.str_time_default, *globs.start_times[1:])
        self.option_time.pack(side = TOP)

        message_priority = Label(self, text="Priority:")
        message_priority.pack(side = TOP)

        self.course_time_priority_default = StringVar(self)
        self.course_time_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self, \
            self.course_time_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)

        self.button_add_course_constraint = Button(self, text="Add Constraint",\
                                                    command=self.add_course_constraint)
        self.button_add_course_constraint.pack(side = RIGHT, pady = 25)

    def add_course_constraint(self):
        """Adds course constraint"""
        course = self.str_course_default.get()
        time_str =  self.str_time_default.get()
        when = self.str_when_default.get()
        priority = self.course_time_priority_default.get()
        create_course_time_constraint(course, time_str, when, priority, self.constraints_view_obj)

    def callback_after_before(self, *args):
        """Toggles changes in the when field"""
        when = self.str_when_default.get()
        menu = self.option_time["menu"]
        menu.delete(0, "end")
        if when == "After":
            start_times = globs.start_times[:-1]
        else:
            start_times = globs.start_times[1:]
        for start_time in start_times :
            menu.add_command(label=start_time,\
                              command=lambda value=start_time : self.str_time_default.set(value))
        self.str_time_default.set(start_times[0])


def get_priority_value(priority):
    """Get priofrity from number from text"""
    if priority == "Low":
        priority = 10
    elif priority == "Medium":
        priority = 25
    elif priority == "High":
        priority = 50
    else:  # mandatory, include a boolean in args
        priority = 0
    return priority

def check_constraint_exists(name):
    """ Checks to see if a constraint_obj name is already found in the
    scheduler's constraint_obj list.
    IN:  A string that is the constraint_obj name
    OUT: 0 if the constraint_obj already exists, 1 if it does not
    """
    for constraint_obj in globs.mainScheduler.constraints:
        if constraint_obj.name == name:
            return 0
    return 1

def constraint_adding_conflict(constraint_name, constraint_list):
    """ Checks a constraint_obj about to be added and determines if it will
    conflict with another constraint_obj already added.
    Example:  CSC 232_before_9, CSC 232_after_9 is pointless, so we don't add
    the new constraint_obj.
    IN:  new constraint_obj name, list of added constraints
    OUT: 0 or 1 if the constraint_obj is bad/good
    """

    new_constraint = constraint_name.split('_')
    if ' ' in new_constraint[0]: # courses have a space ("CSC 111"), instructors don't
        # course constraint_obj
        for constraint_obj in constraint_list:
            old_constraint = constraint_obj.name.split('_')
            if new_constraint[0] == old_constraint[0]: # same course code
                if new_constraint[2] == old_constraint[2]: # same time slot
                    return 0  # can't be duplicate, so the before/after must vary, error
    else:
        # instructor constraint_obj
        for constraint_obj in constraint_list:
            old_constraint = constraint_obj.name.split('_')
            if new_constraint[0] == old_constraint[0]: # same instructor
                if len(new_constraint) == len(old_constraint):
                    # day pref is len = 3, time pref is len = 4
                    if len(new_constraint) == 3:
                        if new_constraint[2] != old_constraint[2]: # different day codes
                            return 0
                    else:  # time pref
                        if new_constraint[3] == old_constraint[3]: # same time slot
                            # only thing that varies is before/after, error
                            return 0
    # if no return 0/error by now, the constraint_obj is fine and doesn't conflict
    return 1

def create_course_time_constraint(course, start_time, when, priority, constraints_view):
    """Creates course time constraint"""
    # convert the priority string to a weight value for fitness score
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    constraint_name = "{0}_{1}_{2}".format(course, when, start_time)

    if check_constraint_exists(constraint_name) == 0:
        tkMessageBox.showerror("Duplicate Constraint", \
                               "This constraint already exists.")
        return

    if constraint_adding_conflict(constraint_name, \
                                  globs.mainScheduler.constraints) == 0:
        tkMessageBox.showerror("Constraint Conflict", \
                               "This constraint conflicts with a previously" \
                               " added constraint.")
        return

    hour, minute = start_time.split(":")
    time_obj = time( int(hour), int(minute) )

    if course not in ["all", "All"]:
        #handle finding the course object in s.courses, assign it to course
        for course_obj in globs.mainScheduler.courses:
            if course_obj.code == course:
                course = course_obj
                break
        if when == "Before":
            globs.mainScheduler.add_constraint(constraint_name, priority,\
                constraint.course_before_time, [course, time_obj, is_mandatory])
        else:  # one course AFTER a time
            globs.mainScheduler.add_constraint(constraint_name, priority,
                                        constraint.course_after_time,
                                         [course, time_obj, is_mandatory])
    else: # applies to all courses
        course = globs.mainScheduler.courses
        if when == "Before":
            globs.mainScheduler.add_constraint(constraint_name, priority,
                                                constraint.all_before_time,
                                                 [course, time_obj, is_mandatory])
        else: # all courses AFTER
            globs.mainScheduler.add_constraint(constraint_name, priority,
                                                constraint.all_after_time,
                                                 [course, time_obj, is_mandatory])

    # update scrollbox with this created constraint
    constraints_view.view_constraints((constraint_name + " Priority = ", priority))
    return
