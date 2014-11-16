from Tkinter import *
from guiClasses import *
from guiConstraintsView import *
from datetime import time
import sys
sys.path.append("../")
import globs
from genetic import constraint
from ScrolledText import ScrolledText  # textbox with scrollbar for view screen
import tkMessageBox


class Page(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

    def show(self):
        self.lift()

class HomeConstraintPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)

        paragraph_text = " Select an option\n"
        self.description_label = Label(self, text=paragraph_text)
        self.description_label.pack()

class InstructorConstraint(Page):

    def __init__(self, root, constraints):
        Frame.__init__(self, root)

        self.constraints = constraints

        instructor_name = Label(self, text = "Instructor name:")
        instructor_name.pack(side = TOP)

        self.str_instr_name_default = StringVar(self)
        list_of_instructors = globs.instructors
        # list_of_instructors.append("All") # necessary?
        self.str_instr_name_default.set(list_of_instructors[0])
        self.option_instructors = OptionMenu(self, self.str_instr_name_default, *list_of_instructors)
        self.option_instructors.pack(side = TOP)

        # time or day toggle box
        label_time_day = Label(self, text = "Type: ")
        label_time_day.pack(side = TOP)
        self.time_day_default = StringVar(self)
        self.time_day_default.set("Time")
        self.time_day_default.trace("w", self.time_day_toggle)
        self.time_day_list = ["Time", "Day", "Computer Preference", "Instructor Break"]
        self.option_time_day = OptionMenu(self, self.time_day_default, \
                                          *self.time_day_list)
        self.option_time_day.pack(side = TOP)

        # dynamically change based on time/day being selected in the toggle


        # time
        self.time_frame = Frame(self)
        self.time_frame.pack()
        self.label_when = Label(self.time_frame, text = "When:")
        self.label_when.pack(side = TOP)

        self.when_default = StringVar(self)
        self.when_default.set("Before")
        self.when_default.trace("w", self.callbackWhen)
        self.when_options = ["Before", "After"]
        self.when_menu = OptionMenu(self.time_frame, self.when_default, *self.when_options)
        self.when_menu.pack(side = TOP)

        self.time_label = Label(self.time_frame, text = "Timeslot:")
        self.time_label.pack(side = TOP)

        self.time_slots = globs.start_times
        self.time_default = StringVar(self)
        self.time_default.set(self.time_slots[1])

        self.time_slot_menu = OptionMenu(self.time_frame, self.time_default, *self.time_slots[1:])
        # default is before so knock out the first slot to avoid invalid constraints
        self.time_slot_menu.pack(side = TOP)

        self.priority_label = Label(self.time_frame, text = "Priority: ")
        self.priority_label.pack()
        self.instr_time_priority_default = StringVar(self)
        self.instr_time_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self.time_frame, \
            self.instr_time_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)

        before_after_disclaimer = "Note: you should not use these constraints to specify a gap (eg, lunch break). \n" \
                                  "If you want a gap, use an Instructor Break constraint."
        self.disclaimer = Label(self.time_frame, text = before_after_disclaimer, wraplength = 180, justify = LEFT)
        self.disclaimer.pack()

        self.submit_time = Button(self.time_frame, text = "Add Constraint", command = self.add_instr_time)
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


        self.submit_day = Button(self.day_frame, text = "Add Constraint", command = self.add_instr_day)
        self.submit_day.pack(side = TOP, pady = 25)

        # computer preference
        self.computer_frame = Frame(self, width = 100)
        # don't pack this because Time is the default option so computers shouldn't be visible

        self.label_computer = Label(self.computer_frame, \
            text = "Instructor would prefer to teach lecture classes in a classroom with computers:", wraplength = 100)
        self.label_computer.pack(side = TOP)

        self.computer_options = ["True", "False"]
        self.computer_radiobutton = StringVar(value = "True")

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
            text = "Add Constraint", command = self.add_instr_computer)
        self.submit_computer.pack(side = TOP, pady = 25)

        # instructor break
        self.break_frame = Frame(self, width = 100)

        self.label_break = Label(self.break_frame, \
                                 text = "Instructor would like no classes between:", wraplength = 120)
        self.label_break.pack(side = TOP)

        self.start_time_list = globs.start_times
        self.end_time_list = globs.end_times

        self.start_time_label = Label(self.break_frame, text = "Start Time:")
        self.start_time_label.pack(side = TOP)
        self.gap_start_default = StringVar()
        self.gap_start_default.set(self.start_time_list[0])
        self.gap_start_default.trace("w", self.callback_gap_start)

        self.gap_start_option = OptionMenu(self.break_frame, \
                                           self.gap_start_default, *self.start_time_list)
        self.gap_start_option.pack(side = TOP)

        self.end_time_label = Label(self.break_frame, text = "End Time:")
        self.end_time_label.pack(side = TOP)
        self.gap_end_default = StringVar()
        self.gap_end_default.set(self.end_time_list[0]) # trace isn't necessary

        self.gap_end_option = OptionMenu(self.break_frame, \
                                         self.gap_end_default, *self.end_time_list)
        self.gap_end_option.pack(side = TOP)

        self.break_priority_label = Label(self.break_frame, text = "Priority")
        self.break_priority_label.pack(side = TOP)
        self.priority_list = ["Low", "Medium", "High", "Mandatory"]
        self.break_priority_default = StringVar()
        self.break_priority_default.set(self.priority_list[0])
        self.break_priority = OptionMenu(self.break_frame, \
                                         self.break_priority_default, *self.priority_list)
        self.break_priority.pack(side = TOP)

        self.submit_break = Button(self.break_frame, \
                                   text = "Add Constraint", command = self.add_instr_break)
        self.submit_break.pack(side = TOP, pady = 25)
        
    def add_instr_break(self):
        instructor = self.str_instr_name_default.get()
        gap_start = self.gap_start_default.get()
        gap_start = self.string_to_time(gap_start)
        gap_end = self.gap_end_default.get()
        gap_end = self.string_to_time(gap_end)
        priority = self.break_priority_default.get()
        create_instr_break(instructor, gap_start, gap_end, priority, self.constraints)
        pass


    def add_instr_time(self):
        instructor = self.str_instr_name_default.get()
        before_after = self.when_default.get()
        timeslot = self.time_default.get()
        priority = self.instr_time_priority_default.get()
        create_time_pref_constraint(instructor, before_after, timeslot, priority, self.constraints)
        pass


    def add_instr_day(self):
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
        pass


    def add_instr_computer(self):
        instructor = self.str_instr_name_default.get()
        radiobutton = self.computer_radiobutton
        if radiobutton.get() == "True": #cannot use bool() because bool("False") -> True
            prefers_computers = True
        else:
            prefers_computers = False
        priority = self.instr_computer_priority_default.get()
        create_computer_pref_constraint(instructor, prefers_computers, priority, self.constraints)
        pass

    def callback_gap_start(self, *args):
        """ Monitors the Instructor Break start time.  If it changes,
        this will update the end time list so that you can't have
        bad end times (before the start time). """
        gap_start = self.gap_start_default.get()
        gap_start = self.string_to_time(gap_start)
        
        end_time_list = globs.end_times
        gap_end_menu = self.gap_end_option["menu"]
        gap_end_menu.delete(0, "end")
        
        for i in range(len(self.end_time_list)):
            end_slot = self.string_to_time(self.end_time_list[i])
            if gap_start <= end_slot: 
                end_time_list = end_time_list[i:]
                break
        for time in end_time_list:
            gap_end_menu.add_command(label = time,
                                     command = lambda value = time : self.gap_end_default.set(value) )
        self.gap_end_default.set(end_time_list[0])


    def string_to_time(self, time_str):
        t_hr, t_min = time_str.split(":")
        return time( int(t_hr), int(t_min) )
        

    def callbackWhen(self, *args):
        when = self.when_default.get()
        menu = self.time_slot_menu["menu"]
        menu.delete(0, "end")
        if when == "After":
            t = globs.start_times[:-1]
        else:
             t = globs.start_times[1:]
        for time in t :
                menu.add_command(label=time, command=lambda value=time : self.time_default.set(value))
        self.time_default.set(t[0])


    def time_day_toggle(self, *args):
        time_day = self.time_day_default.get()
        if time_day == "Day":
            self.time_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.break_frame.pack_forget()
            self.day_frame.pack()
        elif time_day == "Computer Preference":
            self.time_frame.pack_forget()
            self.day_frame.pack_forget()
            self.break_frame.pack_forget()
            self.computer_frame.pack()
        elif time_day == "Instructor Break":
            self.time_frame.pack_forget()
            self.day_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.break_frame.pack()
        else:
            self.time_frame.pack()
            self.day_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.break_frame.pack_forget()


class CourseConstraint(Page):

    def __init__(self, root, constraints):
        Frame.__init__(self, root)

        globs.init()

        self.constraints = constraints

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
        self.str_when_default.trace("w", self.callbackWhen)
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

        self.button_go = Button(self, text="Add Constraint", command=self.go)
        self.button_go.pack(side = RIGHT, pady = 25)

    def go(self):
        course = self.str_course_default.get()
        time =  self.str_time_default.get()
        when = self.str_when_default.get()
        priority = self.course_time_priority_default.get()
        create_course_time_constraint(course, time, when, priority, self.constraints)

    def callbackWhen(self, *args):
        when = self.str_when_default.get()
        menu = self.option_time["menu"]
        menu.delete(0, "end")
        if(when == "After"):
            t = globs.start_times[:-1]
        else:
             t = globs.start_times[1:]
        for time in t :
                menu.add_command(label=time, command=lambda value=time : self.str_time_default.set(value))
        self.str_time_default.set(t[0])

class ConstraintPage(Page):

    def __init__(self, root, constraints):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Constraint Page", \
                                font =('Helvetica', 18))
        self.head_label.pack()
        self.create_widgets()
        self.pack(side = TOP, fill = "both")


        # CONTENT
        self.content_container = Frame(self, width="400", height="300")
        self.content_container.pack(fill="both")

        # PAGES
        self.home_page = HomeConstraintPage(self.content_container)
        #self.home_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        self.home_page.pack(anchor = NW, padx = 50)

        self.constraints_view = ConstraintsView(self.content_container)
        #self.constraints_view.place(in_ = self.instructor_page, anchor = E)
        #self.constraints_view.place(in_ = self.course_page, anchor = E)
        self.constraints_view.pack(side = RIGHT, anchor = NE, padx = 50)

        self.instructor_page = InstructorConstraint(self.content_container, self.constraints_view)
        #self.instructor_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        #self.instructor_page.pack(side = LEFT)

        self.course_page = CourseConstraint(self.content_container, self.constraints_view)
        #self.course_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        #self.course_page.pack(side = LEFT)

        # INITIALIZE WITH HOME PAGE
        self.home_page.lift()

    def add_instructor_constraint(self):
        self.instructor_page.pack(side = LEFT, padx = 50)
        self.course_page.pack_forget()

    def add_course_constraint(self):
        self.course_page.pack(side = LEFT, padx = 50)
        self.instructor_page.pack_forget()

    def create_widgets(self):

        self.button_course = Button(self, text="Add Course Constraint", command=self.add_course_constraint)
        self.button_course.pack(anchor = NW, padx = 50, pady = 10)

        self.button_instructor = Button(self, text="Add Instructor Constraint", command=self.add_instructor_constraint)
        self.button_instructor.pack(anchor = NW, padx = 50)


def get_priority_value(priority):
    if priority == "Low":
        priority = 10
    elif priority == "Medium":
        priority = 25
    elif priority == "High":
        priority = 50
    else:  # mandatory, include a boolean in args
        priority = 0
    return priority


def pull_instructor_obj(instructor):
    for i in range(len(globs.instructors)):
        if instructor == globs.instructors[i].name:  # look for appropriate instructor object
            instructor = globs.instructors[i]
            break
    return instructor


def okay_to_add_constraint(name):
    """
    Checks if constraint is nonduplicate and nonconflicting.
    Calls gui.guiConstraints.check_constraint_exists() and
    gui.guiConstrainsts.constraint_adding_conflict().
    IN: constraint to be added
    OUT: True if constraint is okay to add (ie non-conflicting) else False
    """
    all_constraints = globs.mainScheduler.constraints
    if check_constraint_exists(name) == True:
        tkMessageBox.showerror("Duplicate Constraint", "This constraint already exists.")
        return False
    if constraint_adding_conflict(name, all_constraints) == True:
        tkMessageBox.showerror("Constraint Conflict", \
            "This constraint conflicts with a previously added constraint.")
        return False
    return True


def check_constraint_exists(name):
    """
    Checks to see if a constraint name is already found in the
    scheduler's constraint list.
    IN:  A string that is the constraint name
    OUT: True if the constraint already exists, False if it does not
    """
    for constraint in globs.mainScheduler.constraints:
        if constraint.name == name:
            return True
    return False


def constraint_adding_conflict(constraint_name, constraint_list):
    """
    Checks a constraint about to be added and determines if it will
    conflict with another constraint already added.
    Example:  CSC 232_before_9, CSC 232_after_9 is pointless, so we don't add
    the new constraint.
    IN:  new constraint name, list of added constraints
    OUT: True if new constraint adds conflict, else False
    """

    new_constraint = constraint_name.split('_')
    if len(constraint_list) > 0:        # no need to check first constraint
        # !!! this logic could pontially break if we have an instructor with two last names !!!
        if ' ' in new_constraint[0]:    # courses have a space ("CSC 111"), instructors don't
            # course constraint
            for constraint in constraint_list:
                old_constraint = constraint.name.split('_')
                if new_constraint[0] == old_constraint[0]:      # same course code
                    if new_constraint[2] == old_constraint[2]:  # same time slot; error
                        return True

        else:
            # instructor constraint
            for constraint in constraint_list:
                old_constraint = constraint.name.split('_')
                if new_constraint[0] == old_constraint[0]: # same instructor
                    if len(new_constraint) == len(old_constraint):
                        # day pref is len = 3, time pref is len = 4
                        if len(new_constraint) == 3: # day pref
                            if new_constraint[2] != old_constraint[2]:  # different day codes; conflict
                                return True
                        elif new_constraint[3] in ["before", "after"]:  # time pref
                            if new_constraint[3] == old_constraint[3]:  # same time slot; conflict
                                return True
                        elif new_constraint[2] == "computers":          # computer pref
                            if new_constraint[3] != old_constraint[3]:  # different truthiness; conflict
                                return True
    # if no return True by now, the constraint is fine and doesn't conflict
    return False


def create_course_time_constraint(course, start_time, when, priority, added_constraints):
    # convert the priority string to a weight value for fitness score
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    constraint_name = "{0}_{1}_{2}".format(course, when, start_time)

    if okay_to_add_constraint(constraint_name) == False: return

    hour, minute = start_time.split(":")
    time_obj = time( int(hour), int(minute) )

    if course not in ["all", "All"]:
        #handle finding the course object in s.courses, assign it to course
        for c in globs.mainScheduler.courses:
            if c.code == course:
                course = c
                break
        if when == "Before":
             globs.mainScheduler.add_constraint(constraint_name, priority,
                                                constraint.course_before_time,
                                                 [course, time_obj, is_mandatory])
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
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return


def create_time_pref_constraint(instructor, before_after, timeslot, priority, added_constraints):
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    hour, minute = timeslot.split(":")
    time_obj = time( int(hour), int(minute) )
    constraint_name = "{0}_prefers_{1}_{2}".format(instructor.name, before_after.lower(), str(time_obj))

    if okay_to_add_constraint(constraint_name) == False: return

    if before_after == "Before":
        globs.mainScheduler.add_constraint(constraint_name, priority,
                                           constraint.instructor_time_pref_before,
                                           [instructor, time_obj, is_mandatory])

    else:  # after a time
        globs.mainScheduler.add_constraint(constraint_name, priority,
                                           constraint.instructor_time_pref_after,
                                           [instructor, time_obj, is_mandatory])
        pass

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return


def create_day_pref_constraint(instructor, day_code, priority, added_constraints):
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

    if okay_to_add_constraint(constraint_name) == False: return

    day_code = day_code.lower()
    globs.mainScheduler.add_constraint(constraint_name, priority,
                                       constraint.instructor_preference_day,
                                       [instructor, day_code, is_mandatory])

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return


def create_computer_pref_constraint(instructor, prefers_computers, priority, added_constraints):
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    constraint_name = "{0}_prefers_computers_{1}".format(instructor.name, prefers_computers)

    if okay_to_add_constraint(constraint_name) == False: return

    globs.mainScheduler.add_constraint(constraint_name, priority, \
        constraint.instructor_preference_computer, [instructor, prefers_computers, is_mandatory])

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return

def create_instr_break(instructor, gap_start, gap_end, priority, added_constraints):
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    constraint_name = "{0}_break_{1}-{2}".format(instructor, gap_start, gap_end)
    
    if okay_to_add_constraint(constraint_name) == False: return

    globs.mainScheduler.add_constraint(constraint_name,
                                       priority,
                                       constraint.instructor_break_constraint,
                                       [    instructor,
                                            gap_start,
                                            gap_end,
                                            is_mandatory ]
                                       )
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return
                                    

