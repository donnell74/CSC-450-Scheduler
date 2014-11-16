from Tkinter import Frame, Label, StringVar, OptionMenu, Checkbutton, Button, Radiobutton, IntVar
from Tkconstants import TOP, RIGHT, CENTER
from datetime import time
import globs
from genetic import constraint
import tkMessageBox

class InstructorConstraint(Frame):
    """Instructor constraint frame"""

    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        self.constraints = constraints_view_obj

        instructor_name = Label(self, text="Instructor name:")
        instructor_name.pack(side=TOP)

        self.str_instr_name_default = StringVar(self)
        list_of_instructors = globs.instructors
        # list_of_instructors.append("All") # necessary?
        self.str_instr_name_default.set(list_of_instructors[0])
        self.option_instructors = OptionMenu(self, self.str_instr_name_default,\
                                             *list_of_instructors)
        self.option_instructors.pack(side=TOP)

        # time or day toggle box
        label_time_day = Label(self, text="Type: ")
        label_time_day.pack(side=TOP)
        self.time_day_default = StringVar(self)
        self.time_day_default.set("Time")
        self.time_day_default.trace("w", self.callback_time_day_computer)
        self.time_day_list = ["Time", "Day", "Computer Preference"]
        self.option_time_day = OptionMenu(self, self.time_day_default, \
                                          *self.time_day_list)
        self.option_time_day.pack(side=TOP)

        # dynamically change based on time/day being selected in the toggle
        # time
        self.time_frame = Frame(self)
        self.time_frame.pack()
        self.label_when = Label(self.time_frame, text="When:")
        self.label_when.pack(side=TOP)

        self.when_default = StringVar(self)
        self.when_default.set("Before")
        self.when_default.trace("w", self.callback_after_before)
        self.when_options = ["Before", "After"]
        self.when_menu = OptionMenu(self.time_frame, self.when_default, *self.when_options)
        self.when_menu.pack(side=TOP)

        self.time_label = Label(self.time_frame, text="Timeslot:")
        self.time_label.pack(side = TOP)

        self.time_slots = globs.start_times
        self.time_default = StringVar(self)
        self.time_default.set(self.time_slots[1])

        self.time_slot_menu = OptionMenu(self.time_frame, self.time_default, *self.time_slots[1:])
        # default is before so knock out the first slot to avoid invalid constraints_view_obj
        self.time_slot_menu.pack(side = TOP)

        self.priority_label = Label(self.time_frame, text = "Priority: ")
        self.priority_label.pack()
        self.instr_time_priority_default = StringVar(self)
        self.instr_time_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self.time_frame, \
            self.instr_time_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)

        self.submit_time = Button(self.time_frame, text = "Add Constraint",\
                                   command = self.add_instructor_time)
        self.submit_time.pack(side = RIGHT, pady = 25)

        # day - CHECKBOXES
        self.day_frame = Frame(self, width = 100)
        # don't pack this because Time is the default option so days shouldn't be visible

        self.label_day = Label(self.day_frame, text = "Day(s) instructor prefers to teach:", \
                               wraplength = 100)
        self.label_day.pack(side = TOP)

        self.days = ["M", "T", "W", "R", "F"]
        self.boxes = [IntVar() for i in range(5)]
        for i in range(len(self.days)):
            self.value = self.boxes[i]
            box = Checkbutton(self.day_frame, text = self.days[i], variable = self.value)
            box.pack(side = TOP, anchor = CENTER)

        self.priority_label = Label(self.day_frame, text = "Priority: ")
        self.priority_label.pack()
        self.instr_day_priority_default = StringVar(self)
        self.instr_day_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self.day_frame, \
            self.instr_day_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)

        self.submit_day = Button(self.day_frame, text = "Add Constraint",\
                                  command = self.add_instructor_day)
        self.submit_day.pack(side = TOP, pady = 25)

        # computer preference
        self.computer_frame = Frame(self, width = 100)
        # don't pack this because Time is the default option so computers shouldn't be visible

        self.label_computer = Label(self.computer_frame, \
        text = "Instructor would prefer to teach lecture classes in a classroom with computers:",\
            wraplength = 100)
        self.label_computer.pack(side = TOP)

        self.computer_options = ["True", "False"]
        self.computer_radiobutton = StringVar()
        for i in range(len(self.computer_options)):
            box = Radiobutton(self.computer_frame, text = self.computer_options[i], \
                value = self.computer_options[i], variable = self.computer_radiobutton)
            box.pack(side = TOP, anchor = CENTER)

        self.priority_label = Label(self.computer_frame, text = "Priority: ")
        self.priority_label.pack()

        self.instr_computer_priority_default = StringVar(self)
        self.instr_computer_priority_default.set("Low") # initial value

        self.option_priority = OptionMenu(self.computer_frame, \
            self.instr_computer_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)

        self.submit_computer = Button(self.computer_frame, \
            text = "Add Constraint", command = self.add_instructor_computer)
        self.submit_computer.pack(side = TOP, pady = 25)

    def add_instructor_time(self):
        """Adds instructor time constraint"""
        instructor = self.str_instr_name_default.get()
        before_after = self.when_default.get()
        timeslot = self.time_default.get()
        priority = self.instr_time_priority_default.get()
        create_time_pref_constraint(instructor, before_after, timeslot, priority, self.constraints)

    def add_instructor_day(self):
        """Adds instructor day constraint"""
        instructor = self.str_instr_name_default.get()
        checkboxes = self.boxes
        days = self.days
        day_code = []
        for i in range(len(checkboxes)):  # check each box to see if it's ticked
            if checkboxes[i].get() == 1:  #checked, so push the day to day_code
                day_code.append(days[i])

        day_code = ''.join(day_code)
        priority = self.instr_day_priority_default.get()
        create_day_pref_constraint(instructor, day_code, priority, self.constraints)

    def add_instructor_computer(self):
        """Adds instructor computer constraint"""
        instructor = self.str_instr_name_default.get()
        radiobutton = self.computer_radiobutton
        prefers_computers = bool(radiobutton.get())
        priority = self.instr_computer_priority_default.get()
        create_computer_pref_constraint(instructor, prefers_computers, priority, self.constraints)

    def callback_after_before(self, *args):
        """Toggles the changes in the when field"""
        when = self.when_default.get()
        menu = self.time_slot_menu["menu"]
        menu.delete(0, "end")
        if when == "After":
            list_times = globs.start_times[:-1]
        else:
            list_times = globs.start_times[1:]
        for time_start in list_times :
            menu.add_command(label=time_start,\
                              command=lambda value=time_start : self.time_default.set(value))
        self.time_default.set(list_times[0])

    def callback_time_day_computer(self, *args):
        """Toggles the changes in instructor constraint type field"""
        time_day = self.time_day_default.get()
        if time_day == "Day":
            self.time_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.day_frame.pack()
        elif time_day == "Computer Preference":
            self.time_frame.pack_forget()
            self.day_frame.pack_forget()
            self.computer_frame.pack()
        else:
            self.time_frame.pack()
            self.day_frame.pack_forget()
            self.computer_frame.pack_forget()

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

def create_time_pref_constraint(instructor, before_after, timeslot, priority, constraints_view_obj):
    """Creates time preference constraint"""
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    hour, minute = timeslot.split(":")
    time_obj = time( int(hour), int(minute) )
    constraint_name = "{0}_prefers_{1}_{2}".format(instructor.name, before_after.lower(),\
                                                    str(time_obj))

    if check_constraint_exists(constraint_name) == 0:
        tkMessageBox.showerror("Duplicate Constraint",
                               "This constraint already exists.")
        return

    if constraint_adding_conflict(constraint_name,
                                  globs.mainScheduler.constraints) == 0:
        tkMessageBox.showerror("Constraint Conflict",
                               "This constraint conflicts with a previously" + \
                                " added constraint.")
        return

    if before_after == "Before":
        globs.mainScheduler.add_constraint(constraint_name, priority,
                                           constraint.instructor_time_pref_before,
                                           [instructor, time_obj, is_mandatory])

    else:  # after a time
        globs.mainScheduler.add_constraint(constraint_name, priority,
                                           constraint.instructor_time_pref_after,
                                           [instructor, time_obj, is_mandatory])

    constraints_view_obj.add_constraint_listbox(constraint_name, priority)
    return

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

def create_day_pref_constraint(instructor, day_code, priority, added_constraints):
    """Creates day preference constraint"""
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    if len(day_code) > 4:  # can't select every day of the week, bad constraint
        error_message = "Error, a day preference can't be all days of the week, try again."
        tkMessageBox.showerror("Error", error_message)
        return
    if len(day_code) < 1: # can't pick no days, instructors have to work
        error_message = "Error, a day preference must include at least one day."
        tkMessageBox.showerror("Error", error_message)
        return

    constraint_name = "{0}_prefers_{1}".format(instructor.name, day_code)
    if check_constraint_exists(constraint_name) == 0:
        tkMessageBox.showerror("Duplicate Constraint",
                               "This constraint already exists.")
        return

    if constraint_adding_conflict(constraint_name,
                                  globs.mainScheduler.constraints) == 0:
        tkMessageBox.showerror("Constraint Conflict",
                               "This constraint conflicts with a previously" + \
                                " added constraint.")
        return

    day_code = day_code.lower()
    globs.mainScheduler.add_constraint(constraint_name, priority,
                                       constraint.instructor_preference_day,
                                       [instructor, day_code, is_mandatory])

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return

def pull_instructor_obj(instructor):
    """Get instructor object"""
    for i in range(len(globs.instructors)):
        if instructor == globs.instructors[i].name:  # look for appropriate instructor object
            instructor = globs.instructors[i]
            break
    return instructor

def create_computer_pref_constraint(instructor, prefers_computers, priority, added_constraints):
    """Creates computer preference constraint"""
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    constraint_name = "{0}_prefers_computers_{1}".format(instructor.name, prefers_computers)

    globs.mainScheduler.add_constraint(constraint_name, priority, \
        constraint.instructor_preference_computer, [instructor, prefers_computers, is_mandatory])

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return
