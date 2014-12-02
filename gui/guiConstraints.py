from Tkinter import *
from guiClasses import *
from guiConstraintsView import *
from datetime import time
import sys
from genetic.structures.course import Course
sys.path.append("../")
import globs
from genetic import constraint
from ScrolledText import ScrolledText  # textbox with scrollbar for view screen
import tkMessageBox
from re import match
from copy import deepcopy

#constants
DAY_COURSE = "Day"
ROOM_COURSE = "Room"
TIME = "Time"
MANUAL_CONCURRENCY = "Avoid Overlap"
ROOM_TIME_AVAIL = "Available"

TYPE_DAY_COURSE = 0
TYPE_TIME_COURSE = 1
TYPE_MANUAL_CONCURRENCY = 2
TYPE_TIME_INSTRUCTOR = 3
TYPE_DAY = 4
TYPE_INSTRUCTOR_BREAK = 5
TYPE_MAX_PER_DAY = 6
TYPE_COMPUTER_PREFERENCE = 7
TYPE_ROOM_COURSE = 8
TYPE_ROOM_TIME_AVAIL = 9

class Page(Frame):
    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def __init__(self, root):
        Frame.__init__(self, root)

    def show(self):
        self.lift()

class AddedConstraintsScreen(Page):
    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def __init__(self, root, constraints):
        Frame.__init__(self, root, width = 30, height = 50)
        
        # list that holds Constraint objects
        self.constraints = constraints

        # holds the scrollbox output text for the added constraints
        self.constraint_output = []
        
        textL = " Constraints Added: "
        self.text = Label(self, text = textL)
        self.text.pack(anchor = NW, expand = YES)

        # scrollbox
        self.scroll = ScrolledText(self, undo = True, width = 40, height = 15)
        self.scroll['font'] = ('Courier New', '11')
        self.scroll.pack(fill = BOTH, padx = 5, pady = 5)

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #     
    def view_constraints(self, constraint):
        output = constraint[0]
        #output = output.strip("Constraint Conflict")
        
        if constraint[1] == 10:
            output += 'Low'
        elif constraint[1] == 25:
            output += 'Medium'
        elif constraint[1] == 50:
            output += 'High'
        elif constraint[1] == 100:
            output += 'Mandatory'
            
        output += '\n'
        self.constraint_output.append(output)

        # clear scrollbox
        self.scroll.delete('1.0', END)

        # insert constraint output to scrollbox
        for constraint in self.constraint_output:
            self.scroll.insert(INSERT, constraint)
        
class HomeConstraintPage(Page):
    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def __init__(self, root):
        Frame.__init__(self, root)

        paragraph_text = " Select an option"
        self.description_label = Label(self, text=paragraph_text)
        self.description_label.pack()

class InstructorConstraint(Page):
    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def __init__(self, root, constraints):
        Frame.__init__(self, root)

        self.constraints = constraints
        priority_options = ["Low", "Medium", "High", "Mandatory"]

        instructor_name = Label(self, text = "Instructor name:")
        instructor_name.pack(side = TOP)

        self.str_instr_name_default = StringVar(self)
        list_of_instructors = globs.instructors
        # list_of_instructors.append("All") # necessary?
        self.str_instr_name_default.set(list_of_instructors[0])
        self.option_instructors = OptionMenu(self, self.str_instr_name_default, *list_of_instructors)
        self.option_instructors.pack(side = TOP)

        # type of Constraint toggle box
        constraint_type_label = Label(self, text = "Type: ")
        constraint_type_label.pack(side = TOP)
        self.constraint_type_choice = StringVar(self)
        self.constraint_type_choice.set("Time")
        self.constraint_type_choice.trace("w", self.constraint_type_toggle)
        self.constraint_type_list = ["Time", "Day", "Computer Preference", "Instructor Break", "Max Per Day"]
        self.constraint_type_menu = OptionMenu(self, self.constraint_type_choice, *self.constraint_type_list)
        self.constraint_type_menu.pack(side = TOP)

        # time
        self.time_frame = Frame(self)
        self.time_frame.pack()

        description_constraint_label_time = Label(self.time_frame, 
                                                  text=get_description_constraint(TYPE_TIME_INSTRUCTOR),
                                                  wraplength = 100)
        description_constraint_label_time.pack(side = TOP)

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
        self.option_priority = OptionMenu(self.time_frame,
                                          self.instr_time_priority_default,
                                          *priority_options)
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

        description_constraint_label_day = Label(self.day_frame,
                                                 text=get_description_constraint(TYPE_DAY),
                                                 wraplength = 100)
        description_constraint_label_day.pack(side = TOP)

#         self.label_day = Label(self.day_frame,
#                                text = "Day(s) instructor prefers to teach:",
#                                wraplength = 100)
#         self.label_day.pack(side = TOP)

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
        self.option_priority = OptionMenu(self.day_frame,
                                          self.instr_day_priority_default,
                                          *priority_options)
        self.option_priority.pack(side = TOP)


        self.submit_day = Button(self.day_frame, text = "Add Constraint", command = self.add_instr_day)
        self.submit_day.pack(side = TOP, pady = 25)

        # computer preference
        self.computer_frame = Frame(self, width = 100)
        # don't pack this because Time is the default option so computers shouldn't be visible

        self.label_computer = Label(self.computer_frame, \
            text = get_description_constraint(TYPE_COMPUTER_PREFERENCE), wraplength = 100)
        self.label_computer.pack(side = TOP)

        self.computer_options = ["True", "False"]
        self.computer_radiobutton = StringVar(value = "True")

        for i in range(len(self.computer_options)):
            box = Radiobutton(self.computer_frame,
                              text = self.computer_options[i],
                              value = self.computer_options[i],
                              variable = self.computer_radiobutton)
            box.pack(side = TOP, anchor = CENTER)

        self.priority_label = Label(self.computer_frame, text = "Priority: ")
        self.priority_label.pack()

        self.instr_computer_priority_default = StringVar(self)
        self.instr_computer_priority_default.set("Low") # initial value

        self.option_priority = OptionMenu(self.computer_frame,
                                          self.instr_computer_priority_default,
                                          *priority_options)
        self.option_priority.pack(side = TOP)

        self.submit_computer = Button(self.computer_frame, text = "Add Constraint", command = self.add_instr_computer)
        self.submit_computer.pack(side = TOP, pady = 25)
        
        # ADD MAX PER DAY STUFFS HERE
        self.max_course_frame = Frame(self, width=100)

        description_constraint_label_max = Label(self.max_course_frame,
                                                 text=get_description_constraint(TYPE_MAX_PER_DAY),
                                                 wraplength = 100)
        description_constraint_label_max.pack(side = TOP)

        self.max_course_value = StringVar()
        self.max_course_value.set("0")
        self.max_course_value.trace("w", self.check_is_digit)
        self.max_course_input = Entry(self.max_course_frame,
                                      textvariable=self.max_course_value,
                                      width=5)
        self.max_course_input.pack(pady=10)

        self.max_course_priority_label = Label(self.max_course_frame,
                                               text="Priority")
        self.max_course_priority_label.pack()
        self.max_course_priority_choice = StringVar()
        self.max_course_priority_choice.set("Low")
        self.option_priority = OptionMenu(self.max_course_frame,
                                          self.max_course_priority_choice,
                                          *priority_options)
        self.option_priority.pack(side = TOP)

        self.max_course_submit = Button(self.max_course_frame,
                                        text="Add Constraint",
                                        command=self.add_max_course)
        self.max_course_submit.pack(side=TOP, pady=25)

        # instructor break
        self.break_frame = Frame(self, width = 100)

        self.label_break = Label(self.break_frame,
                                 text = get_description_constraint(TYPE_INSTRUCTOR_BREAK),
                                 wraplength = 120)
        self.label_break.pack(side = TOP)

        self.start_time_list = globs.start_times
        self.end_time_list = globs.end_times

        self.start_time_label = Label(self.break_frame, text = "Start Time:")
        self.start_time_label.pack(side = TOP)
        self.gap_start_default = StringVar()
        self.gap_start_default.set(self.start_time_list[0])
        self.gap_start_default.trace("w", self.callback_gap_start)

        self.gap_start_option = OptionMenu(self.break_frame,
                                           self.gap_start_default,
                                           *self.start_time_list)
        self.gap_start_option.pack(side = TOP)

        self.end_time_label = Label(self.break_frame, text = "End Time:")
        self.end_time_label.pack(side = TOP)
        self.gap_end_default = StringVar()
        self.gap_end_default.set(self.end_time_list[0]) # trace isn't necessary

        self.gap_end_option = OptionMenu(self.break_frame,
                                         self.gap_end_default,
                                         *self.end_time_list)
        self.gap_end_option.pack(side = TOP)

        self.break_priority_label = Label(self.break_frame, text = "Priority")
        self.break_priority_label.pack(side = TOP)

        self.break_priority_default = StringVar()
        self.break_priority_default.set(priority_options[0])
        self.break_priority_option = OptionMenu(self.break_frame,
                                         self.break_priority_default,
                                         *priority_options)
        self.break_priority_option.pack(side = TOP)

        self.submit_break = Button(self.break_frame,
                                   text = "Add Constraint",
                                   command = self.add_instr_break)
        self.submit_break.pack(side = TOP, pady = 25)


    def check_is_digit(self, *args):
        self.max_course_input.config(state=DISABLED)
        value = self.max_course_value.get()
        for char in value:
            if not char.isdigit():
                self.max_course_value.set(value[:-1])
                tkMessageBox.showerror(title="Error", message="Value must be a number")
                self.max_course_input.config(state=NORMAL)
                return 0
        self.max_course_input.config(state=NORMAL)
        return 1


    def add_instr_break(self):
        instructor = self.str_instr_name_default.get()
        gap_start = self.gap_start_default.get()
        gap_start = self.string_to_time(gap_start)
        gap_end = self.gap_end_default.get()
        gap_end = self.string_to_time(gap_end)
        priority = self.break_priority_default.get()
        create_instr_break(instructor, gap_start, gap_end, priority, self.constraints)
        return

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def add_instr_time(self):
        instructor = self.str_instr_name_default.get()
        before_after = self.when_default.get()
        timeslot = self.time_default.get()
        priority = self.instr_time_priority_default.get()
        create_time_pref_constraint(instructor, before_after, timeslot, priority, self.constraints)
        return


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
        return

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def add_instr_computer(self):
        instructor = self.str_instr_name_default.get()
        radiobutton = self.computer_radiobutton
        if radiobutton.get() == "True": #cannot use bool() because bool("False") -> True
            prefers_computers = True
        else:
            prefers_computers = False
        priority = self.instr_computer_priority_default.get()
        create_computer_pref_constraint(instructor, prefers_computers, priority, self.constraints)
        return


    def add_max_course(self):
        instructor = self.str_instr_name_default.get()
        max_courses = int(self.max_course_value.get())
        priority = self.max_course_priority_choice.get()
        create_max_course_constraint(instructor, max_courses, priority, self.constraints)
        return

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

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def constraint_type_toggle(self, *args):
        constraint_type = self.constraint_type_choice.get()
        if constraint_type == "Day":
            self.time_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.max_course_frame.pack_forget()
            self.break_frame.pack_forget()
            self.day_frame.pack()
        elif constraint_type == "Computer Preference":
            self.time_frame.pack_forget()
            self.day_frame.pack_forget()
            self.max_course_frame.pack_forget()
            self.break_frame.pack_forget()
            self.computer_frame.pack()
        elif constraint_type == "Max Per Day":
            self.time_frame.pack_forget()
            self.day_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.break_frame.pack_forget()
            self.max_course_frame.pack()
        elif constraint_type == "Instructor Break":
            self.time_frame.pack_forget()
            self.day_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.max_course_frame.pack_forget()
            self.break_frame.pack()
        else: # time constraint
            self.day_frame.pack_forget()
            self.computer_frame.pack_forget()
            self.max_course_frame.pack_forget()
            self.break_frame.pack_forget()
            self.time_frame.pack()

class CourseConstraint(Page):
    """Course constraint frame"""

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        #globs.init()

        message_type = Label(self, text="Type:")
        message_type.pack(side = TOP)

        self.str_type_default = StringVar(self)
        self.str_type_default.set(TIME)
        self.str_type_default.trace("w", self.callback_type)
        self.option_type = OptionMenu(self, self.str_type_default, TIME, ROOM_COURSE, \
                                      DAY_COURSE, MANUAL_CONCURRENCY)
        self.option_type.pack(side = TOP)

        self.course_container = Frame(self)
        self.course_container.pack(fill=BOTH, side = TOP)

        # PAGES
        self.type_time_page = TypeTime(self.course_container, constraints_view_obj)
        self.type_time_page.pack()

        self.type_room_course_page = TypeRoomCourse(self.course_container, \
                                                    constraints_view_obj)

        self.type_day_course_page = TypeDayCourse(self.course_container, \
                                                  constraints_view_obj)

        self.type_manual_concurrency_page = TypeManualConcurrency(self.course_container,\
                                                                 constraints_view_obj)

        # INITIALIZE WITH type time
        self.type_time_page.lift()

    def callback_type(self, *args):
        constraint_type_str = self.str_type_default.get()

        if constraint_type_str == TIME:
            self.type_time_page.pack()

            self.type_day_course_page.pack_forget()
            self.type_room_course_page.pack_forget()
            self.type_manual_concurrency_page.pack_forget()

        elif constraint_type_str == MANUAL_CONCURRENCY:
            self.type_manual_concurrency_page.pack()

            self.type_time_page.pack_forget()
            self.type_day_course_page.pack_forget()
            self.type_room_course_page.pack_forget()

        elif constraint_type_str == DAY_COURSE:
            self.type_day_course_page.pack()

            self.type_room_course_page.pack_forget()
            self.type_time_page.pack_forget()
            self.type_manual_concurrency_page.pack_forget()

        elif constraint_type_str == ROOM_COURSE:
            self.type_room_course_page.pack()

            self.type_day_course_page.pack_forget()
            self.type_time_page.pack_forget()
            self.type_manual_concurrency_page.pack_forget()

            
class RoomConstraint(Page):
    """Course constraint frame"""

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        #globs.init()

        message_type = Label(self, text="Type:")
        message_type.pack(side = TOP)

        self.str_type_default = StringVar(self)
        self.str_type_default.set(ROOM_TIME_AVAIL)
        self.str_type_default.trace("w", self.callback_type)
        self.option_type = OptionMenu(self, self.str_type_default, ROOM_TIME_AVAIL)
        self.option_type.pack(side = TOP)

        self.room_container = Frame(self)
        self.room_container.pack(fill=BOTH, side = TOP)
        
        # PAGES
        self.room_time_avail_page = RoomTimeAvail(self.room_container, constraints_view_obj)
        self.room_time_avail_page.pack()

        self.room_time_avail_page.lift()

    def callback_type(self, *args):
        constraint_type_str = self.str_type_default.get()

        if constraint_type_str == ROOM_TIME_AVAIL:
            self.room_time_avail_page.pack()

            
class RoomTimeAvail(Frame):
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        self.constraints_view_obj = constraints_view_obj

        description_constraint_label = Label(self, text=get_description_constraint(TYPE_ROOM_TIME_AVAIL))
        description_constraint_label.pack(side = TOP)

        self.listbox_frame = Frame(self)
        self.listbox_frame.pack(side = TOP)
        
        self.scrollbar = Scrollbar(self.listbox_frame, orient=VERTICAL)
        self.listbox = Listbox(self.listbox_frame, yscrollcommand = self.scrollbar.set,\
                                selectmode = MULTIPLE, height=3)

        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side=LEFT, fill=X, expand=1)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.list_of_rooms = globs.rooms

        for item in self.list_of_rooms:
            self.listbox.insert(END, item[0:2])
            
        self.str_when_default = StringVar(self)
        self.str_when_default.set("Available")
        self.option_when = OptionMenu(self, self.str_when_default, "Available", "Not Available")
        self.option_when.pack(side = TOP)
    
        self.start_time_list = globs.start_times
        self.end_time_list = globs.end_times

        self.start_time_label = Label(self, text = "Start Time:")
        self.start_time_label.pack(side = TOP)
        self.gap_start_default = StringVar()
        self.gap_start_default.set(self.start_time_list[0])
        self.gap_start_default.trace("w", self.callback_gap_start)

        self.gap_start_option = OptionMenu(self,
                                           self.gap_start_default,
                                           *self.start_time_list)
        self.gap_start_option.pack(side = TOP)

        self.end_time_label = Label(self, text = "End Time:")
        self.end_time_label.pack(side = TOP)
        self.gap_end_default = StringVar()
        self.gap_end_default.set(self.end_time_list[0]) # trace isn't necessary

        self.gap_end_option = OptionMenu(self,
                                         self.gap_end_default,
                                         *self.end_time_list)
        self.gap_end_option.pack(side = TOP)

        self.end_time_label = Label(self, text = "On Days:")
        self.end_time_label.pack(side = TOP)        
        self.checkboxes_days = Frame(self)
        self.days = ["M", "T", "W", "R", "F"]
        self.boxes = [IntVar() for i in range(5)]
        for i in range(len(self.days)):
            self.value = self.boxes[i]
            box = Checkbutton(self.checkboxes_days, text = self.days[i], variable = self.value)
            box.pack(side= LEFT, anchor= W, expand=False)

        self.checkboxes_days.pack()
        self.button_add_course_constraint = Button(self, text="Add Availability",\
                                            command=self.add_room_avail)
        self.button_add_course_constraint.pack(side = LEFT, anchor = SW, expand=YES, fill="both")


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
        
    def add_room_avail(self):
        selection = self.listbox.curselection()
        if len(selection) > 0:
            list_rooms = []
            for i in selection :
                list_rooms.append(self.list_of_rooms[int(i)])

            self.listbox.selection_clear(0, END)

            is_avail = self.str_when_default.get() == "Available"
            
            checkboxes = self.boxes
            day_code = []
            for i in range(len(checkboxes)):  # check each box to see if it's ticked
                if checkboxes[i].get() == 1:  #checked, so push the day to day_code
                    day_code.append(self.days[i])

            day_code = ''.join(day_code)
            
            gap_start = self.gap_start_default.get()
            gap_end = self.gap_end_default.get()

            create_room_avail(is_avail, day_code, list_rooms, gap_start,
                              gap_end, self.constraints_view_obj)
        else:
            tkMessageBox.showerror(title="Error", message="Select at least 1 room")
        return

def create_room_avail(is_avail, days, rooms, gap_start, gap_end, constraints_view_obj):
    rooms = [r[0] + "" + r[1] for r in rooms]
        
    for each_room in rooms:
        globs.mainScheduler.add_room_avail(each_room, is_avail, days, gap_start, gap_end)

        constraint_name = each_room + "_"
        constraint_name += "Avail" if is_avail else "NotAvail"
        constraint_name += "_" + gap_start + "_" + gap_end + "_" + days
        constraints_view_obj.add_constraint_listbox(constraint_name, 0)
            

class TypeTime(Frame):
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        self.constraints_view_obj = constraints_view_obj

        description_constraint_label = Label(self, text=get_description_constraint(TYPE_TIME_COURSE))
        description_constraint_label.pack(side = TOP)

        message_course = Label(self, text="Course code:")
        message_course.pack(side = TOP)

        self.str_course_default = StringVar(self)
        list_of_courses = deepcopy(globs.courses)
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

    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #      
    def add_course_constraint(self):
        """Adds course constraint"""
        course = self.str_course_default.get()
        time_str =  self.str_time_default.get()
        when = self.str_when_default.get()
        priority = self.course_time_priority_default.get()
        create_course_time_constraint(course, time_str, when, priority, self.constraints_view_obj)

    ##
    #  @param self
    #  @param __init__ Building a constriant page
    #  
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

class TypeManualConcurrency(Frame):
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        self.constraints_view_obj = constraints_view_obj
        
        description_constraint_label = Label(self, text=get_description_constraint(TYPE_MANUAL_CONCURRENCY), wraplength = 200)
        description_constraint_label.pack(side = TOP)

        self.outside_course_label = Label(self, text="Code of course outside department:", wraplength = 200)
        self.outside_course_label.pack(side = TOP)

        self.outside_course_name = StringVar()
        self.outside_course_name.trace("w", self.check_is_outside_course_name)
        self.outside_course_input = Entry(self,
                                      textvariable=self.outside_course_name,
                                      width=8)
        self.outside_course_input.pack(side = TOP)

        #times
        self.start_time_list = globs.start_times
        self.end_time_list = globs.end_times

        self.start_time_label = Label(self, text = "Start:")
        self.start_time_label.pack(side = TOP)
        self.time_start_default = StringVar()
        self.time_start_default.set(self.start_time_list[0])
 
        self.start_option = OptionMenu(self, \
                                           self.time_start_default, *self.start_time_list)
        self.start_option.pack(side = TOP)
 
        self.end_time_label = Label(self, text = "End:")
        self.end_time_label.pack(side = TOP)
        self.end_default = StringVar()
        self.end_default.set(self.end_time_list[0]) 
 
        self.end_option = OptionMenu(self, \
                                         self.end_default, *self.end_time_list)
        self.end_option.pack(side = TOP)

        #Course listbox
        self.message_course = Label(self, text="Courses to not overlap with:", wraplength = 200)
        self.message_course.pack(side = TOP)
        
        self.listbox_frame = Frame(self)
        self.listbox_frame.pack(side = TOP)
        
        self.scrollbar = Scrollbar(self.listbox_frame, orient=VERTICAL)
        self.listbox = Listbox(self.listbox_frame, yscrollcommand = self.scrollbar.set,\
                                selectmode = MULTIPLE, height=5)

        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side=LEFT, fill=X, expand=1)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.list_of_courses = []
        for course in globs.courses:
            if isinstance(course, Course):
                self.list_of_courses.append(course)


        for item in self.list_of_courses:
            self.listbox.insert(END, item)
        
        priority_options = ["Low", "Medium", "High", "Mandatory"]
        self.priority_label = Label(self, text = "Priority: ")
        self.priority_label.pack()
        self.str_priority_default = StringVar(self)
        self.str_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self,
                                          self.str_priority_default,
                                          *priority_options)
        self.option_priority.pack(side = TOP)
 
        self.button_add_course_constraint = Button(self, text="Add Constraint",\
                                            command=self.add_course_constraint)
        self.button_add_course_constraint.pack(side = BOTTOM, pady = 25)

    def add_course_constraint(self):
        """Adds course constraint"""
        selection = self.listbox.curselection()
        if len(selection) > 0:
            list_courses_obj = []
            for i in selection :
                list_courses_obj.append(self.list_of_courses[int(i)])

            self.listbox.selection_clear(0, END)
            
            priority = self.str_priority_default.get()
            priority = get_priority_value(priority)

            outside_course_name = self.outside_course_name.get()

            gap_start = self.string_to_time(self.time_start_default.get())
            gap_end = self.string_to_time(self.end_default.get())
            
            create_manual_concurrency_constraint(list_courses_obj, priority,
                self.constraints_view_obj, outside_course_name, gap_start, gap_end)
        else:
            tkMessageBox.showerror(title="Error", message="Select at least 1 course")

    def string_to_time(self, time_str):
        t_hr, t_min = time_str.split(":")
        return time( int(t_hr), int(t_min) )

    def check_is_outside_course_name(self, *args):
        self.outside_course_input.config(state=DISABLED)
        value = self.outside_course_name.get()
        for idx, char in enumerate(value):
            if not match(r'\w+$', char): #alphanumeric and _ accepted; all else is not
                self.outside_course_name.set(value[:-1])
                tkMessageBox.showerror(title="Error",
                    message="Value must be alphanumeric or underscore")
                self.outside_course_input.config(state=NORMAL)
                return 0
            elif idx > 7:
                self.outside_course_name.set(value[:-1])
                tkMessageBox.showerror(title="Error",
                    message="Value must be at most 7 characters long")
                self.outside_course_input.config(state=NORMAL)
                return 0
        self.outside_course_input.config(state=NORMAL)
        return 1


def create_manual_concurrency_constraint(list_courses_obj, priority, constraints_view_obj,
                                         outside_course_name, gap_start, gap_end):
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    constraint_name = "avoid overlap"
    constraint_name += "_" + outside_course_name
    constraint_name += "_" + list_courses_obj[0].code
    if len(list_courses_obj) > 1:
        constraint_name += "..."

    if okay_to_add_constraint(constraint_name) == False: return

    globs.mainScheduler.add_constraint(constraint_name,
                                       priority,
                                       constraint.avoid_overlap,
                                       [    list_courses_obj,
                                            gap_start,
                                            gap_end,
                                            is_mandatory]
                                       )

    constraints_view_obj.add_constraint_listbox(constraint_name, priority)

def create_day_course_constraint(course, days, priority, constraints_view_obj):
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    # from course string to course object
    for each_course in globs.courses:
        if each_course.code == course:
            course = each_course
            break

    constraint_name = course.code + "_" + days

    if okay_to_add_constraint(constraint_name) == False: return

    days = days.lower()

    globs.mainScheduler.add_constraint(constraint_name,
                                       priority,
                                       constraint.partial_schedule_day,
                                       [    course,
                                            days,
                                            is_mandatory]
                                       )

    constraints_view_obj.add_constraint_listbox(constraint_name, priority)

def create_room_course_constraint(course, rooms, priority, constraints_view_obj):
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    # from course string to course object
    for each_course in globs.courses:
        if each_course.code == course:
            course = each_course
            break

    rooms = [r[0] + " " + r[1] for r in rooms]

    constraint_name = course.code + "_" + rooms[0]
    if len(rooms) > 1:
        constraint_name += "..."

    if okay_to_add_constraint(constraint_name) == False: return

    globs.mainScheduler.add_constraint(constraint_name,
                                       priority,
                                       constraint.partial_schedule_room,
                                       [    course,
                                            rooms,
                                            is_mandatory]
                                       )

    constraints_view_obj.add_constraint_listbox(constraint_name, priority)

class TypeDayCourse(Frame):
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        self.constraints_view_obj = constraints_view_obj
        description_constraint_label = Label(self,
            text=get_description_constraint(TYPE_DAY_COURSE), wraplength=100)
        description_constraint_label.pack(side = TOP)

        message_course = Label(self, text="Course code:")
        message_course.pack(side = TOP)

        self.str_course_default = StringVar(self)
        self.list_of_courses = globs.courses
        self.str_course_default.set(self.list_of_courses[0])
        self.option_course = OptionMenu(self, self.str_course_default, *self.list_of_courses)
        self.option_course.pack(side = TOP)

        label_days = Label(self, text="Days:")
        label_days.pack(side = TOP)
        
        list_days_str = self.match_days_by_course(self.list_of_courses[0])
        
        self.str_day_default = StringVar(self)
        self.str_day_default.set(list_days_str[0])
        #self.str_day_default.trace("w", self.callback_after_before)
        self.option_day = OptionMenu(self, self.str_day_default, *list_days_str)
        self.option_day.pack(side = TOP)

        priority_options = ["Low", "Medium", "High", "Mandatory"]
        self.priority_label = Label(self, text = "Priority: ")
        self.priority_label.pack()
        self.str_priority_default = StringVar(self)
        self.str_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self,
                                          self.str_priority_default,
                                          *priority_options)
        self.option_priority.pack(side = TOP)

        self.button_add_course_constraint = Button(self, text="Add Constraint",\
                                            command=self.add_course_constraint)
        self.button_add_course_constraint.pack(side = BOTTOM, pady = 25)

    def add_course_constraint(self):
        """Adds course constraint"""
        priority = self.str_priority_default.get()
        priority = get_priority_value(priority)

        course = self.str_course_default.get()

        days = self.str_day_default.get()

        create_day_course_constraint(course, days, priority, self.constraints_view_obj)

    def match_days_by_course(self, course_obj):
        if course_obj.credit == 4:
            list_days_str = ["MTWF", "MWRF"]
            return list_days_str
        elif course_obj.credit == 3:
            list_days_str = ["MWF", "TR"]
            return list_days_str
        elif course_obj.credit == 1 and not course_obj.is_lab:
            list_days_str = ["M", "T", "W", "R", "F"]
            return list_days_str
        elif course_obj.credit == 1 and course_obj.is_lab:
            list_days_str = ["T", "R"]
            return list_days_str


class TypeRoomCourse(Frame):
    def __init__(self, root, constraints_view_obj):
        Frame.__init__(self, root)

        self.constraints_view_obj = constraints_view_obj
        description_constraint_label = Label(self,
            text=get_description_constraint(TYPE_DAY_COURSE), wraplength=100)
        description_constraint_label.pack(side = TOP)

        message_course = Label(self, text="Course code:")
        message_course.pack(side = TOP)

        self.str_course_default = StringVar(self)
        self.list_of_courses = globs.courses
        self.str_course_default.set(self.list_of_courses[0])
        self.option_course = OptionMenu(self, self.str_course_default, *self.list_of_courses)
        self.option_course.pack(side = TOP)

        message_course = Label(self, text="Rooms to schedule on")
        message_course.pack(side = TOP)

        self.listbox_frame = Frame(self)
        self.listbox_frame.pack(side = TOP)
        
        self.scrollbar = Scrollbar(self.listbox_frame, orient=VERTICAL)
        self.listbox = Listbox(self.listbox_frame, yscrollcommand = self.scrollbar.set,\
                                selectmode = MULTIPLE, height=5)

        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side=LEFT, fill=X, expand=1)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.list_of_rooms = globs.rooms

        for item in self.list_of_rooms:
            self.listbox.insert(END, item[0:2])

        priority_options = ["Low", "Medium", "High", "Mandatory"]
        self.priority_label = Label(self, text = "Priority: ")
        self.priority_label.pack()
        self.str_priority_default = StringVar(self)
        self.str_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self,
                                          self.str_priority_default,
                                          *priority_options)
        self.option_priority.pack(side = TOP)

        self.button_add_course_constraint = Button(self, text="Add Constraint",\
                                            command=self.add_course_constraint)
        self.button_add_course_constraint.pack(side = BOTTOM, pady = 25)

    def add_course_constraint(self):
        """Adds course constraint"""
        selection = self.listbox.curselection()
        if len(selection) > 0:
            list_rooms = []
            for i in selection :
                list_rooms.append(self.list_of_rooms[int(i)])

            self.listbox.selection_clear(0, END)
            priority = self.str_priority_default.get()
            priority = get_priority_value(priority)

            course = self.str_course_default.get()

            create_room_course_constraint(course, list_rooms, priority, self.constraints_view_obj)
        else:
            tkMessageBox.showerror(title="Error", message="Select at least 1 room")

class ConstraintPage(Page):
    ## 
    #  @param self
    #  @param __init__ Building a constriant page
    #  
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
        self.home_page.pack(anchor = NW, padx = 50)

        self.constraints_view = ConstraintsView(self.content_container)
        if len(globs.mainScheduler.constraints) > globs.mainScheduler.num_hard_constraints:
            for i in range(globs.mainScheduler.num_hard_constraints, len(globs.mainScheduler.constraints)):
                constraint_name = globs.mainScheduler.constraints[i].name
                priority = globs.mainScheduler.constraints[i].weight
                self.constraints_view.add_constraint_listbox(constraint_name, priority)
        self.constraints_view.pack(side = RIGHT, anchor = NE, padx = 50)

        self.instructor_page = InstructorConstraint(self.content_container, self.constraints_view)

        #self.instructor_page.pack(side = LEFT)

        self.course_page = CourseConstraint(self.content_container, self.constraints_view)

        #self.course_page.pack(side = LEFT)

        self.room_page = RoomConstraint(self.content_container, self.constraints_view)
        
        # INITIALIZE WITH HOME PAGE
        self.home_page.lift()

    ## Adding a instructor constraint 
    #  @param self
    #  @param add_instructor A instructor object 
    #       
    def add_instructor_constraint(self):
        self.instructor_page.pack(side = LEFT, padx = 50)
        self.course_page.pack_forget()
        self.room_page.pack_forget()

    ## Adding a course constraint 
    #  @param self
    #  @param add_instructor A course object 
    #           
    def add_course_constraint(self):
        self.course_page.pack(side = LEFT, padx = 50)
        self.instructor_page.pack_forget()
        self.room_page.pack_forget()

    ## Adding a course constraint 
    #  @param self
    #  @param add_instructor A course object 
    #           
    def add_room_constraint(self):
        self.room_page.pack(side = LEFT, padx = 50)
        self.instructor_page.pack_forget()
        self.course_page.pack_forget()
        
        
    ## Creating a widget  
    #  @param self
    #  @param create_widget Adding a widget 
    #           
    def create_widgets(self):

        self.button_course = Button(self, text="Add Course Constraint", command=self.add_course_constraint)
        self.button_course.pack(anchor = NW, padx = 50, pady = 10)

        self.button_instructor = Button(self, text="Add Instructor Constraint", command=self.add_instructor_constraint)
        self.button_instructor.pack(anchor = NW, padx = 50)

        self.button_room = Button(self, text="Add Room Constraint", command=self.add_room_constraint)
        self.button_room.place(x = 230, y = 41.5 )

        
## Looking for a priority value
#  
#  @param get_priority_object A priority object 
#  @return get_priority_value Priority levels
def get_priority_value(priority):
    priorities = {"Low": 10,
                  "Medium": 25,
                  "High": 50
                  }
    # Look up number value from dict. Return 0 if mandatory
    priority = priorities.get(priority, 0)
    return priority


## Looking for a particular instructor
#  
#  @param pull_instructor_object A instructor object 
#  @return pull_instructor Instructors 
def pull_instructor_obj(instructor):
    for i in range(len(globs.instructors)):
        if instructor == globs.instructors[i].name:  # look for appropriate instructor object
            instructor = globs.instructors[i]
            break
    return instructor

## Creates a course_time constraint
#  
#  @param create_course_time_constrainst A course is set to be taught at specific times
#  @return List_of_course_times A list of times in a day a course is taught  
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
    OUT: 0 or 1 if the constraint is bad/good
    """

    new_constraint = constraint_name.split('_')
    if len(constraint_list) > 0:        # no need to check first constraint
        # !!! this logic could potentially break if we have an instructor with two last names !!!
        if ' ' in new_constraint[0]:    # courses have a space ("CSC 111"), instructors don't
            # course constraint
            for constraint in constraint_list:
                old_constraint = constraint.name.split('_')
                if new_constraint[0] == old_constraint[0]:      # same course code
                    try:
                        if new_constraint[2] == old_constraint[2]:  # same time slot; error
                            return True
                    except IndexError:
                        pass

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
                        elif new_constraint[2] in ["before", "after"]:  # time pref
                            if new_constraint[3] == old_constraint[3]:  # same time slot; conflict
                                return True
                            else: # check if it overlaps a break constraint
                                if old_constraint[1] == "break":
                                    if new_constraint[3] in [old_constraint[2], old_constraint[3]]:
                                        # on edge, not in break, it's fine
                                        continue
                                    else: # not on edge, check for conflict
                                        if new_constraint[3] < old_constraint[3]:
                                            if new_constraint[3] > old_constraint[2]:
                                                # in break, conflict
                                                return True
                        elif new_constraint[2] == "computers":          # computer pref
                            if old_constraint[2] == "computers":
                                if new_constraint[3] != old_constraint[3]:  # different truthiness; conflict
                                    return True
                        elif new_constraint[1] == "break":              # break constraint
                            if old_constraint[3] in [new_constraint[2], new_constraint[3]]: 
                                # if it's on the edge of one of the break times, it's fine
                                continue
                            else:  # old_constraint's time is not one of the break edges
                                if old_constraint[3] < new_constraint[3]: # less than break end
                                    if old_constraint[3] > new_constraint[2]: 
                                        # in break, conflict
                                        return True
                        elif new_constraint[1] == "max":                # max courses
                            if old_constraint[1] == "max":
                                # duplicates are already caught, so max_courses conflicts
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
    added_constraints.add_constraint_listbox(constraint_name, priority)
    return


## Creates a time preference constraint
#  
#  @param create_time_preference A instructor will have the option on what times to lecture
#  @return List_of_times A list of times in a day  
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
        

    # update scrollbox with this created constraint
    added_constraints.add_constraint_listbox(constraint_name, priority)
    return

## Creates a day preference constraint
#  
#
#  @param create_day_preference A instructor will have the option on what days to lecture
#  @return List_of_days A list of days in a week  
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
    added_constraints.add_constraint_listbox(constraint_name, priority)
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
    added_constraints.add_constraint_listbox(constraint_name, priority)
    return

def create_max_course_constraint(instructor, max_courses, priority, added_constraints):
    priority = get_priority_value(priority)
    is_mandatory = (priority == 0)
    instructor = pull_instructor_obj(instructor)

    constraint_name = "{0}_max_courses_{1}".format(instructor.name, max_courses)

    if okay_to_add_constraint(constraint_name) == False: return

    globs.mainScheduler.add_constraint(constraint_name, priority,
                                       constraint.instructor_max_courses,
                                       [instructor, max_courses, is_mandatory])
    added_constraints.add_constraint_listbox(constraint_name, priority)
    return

def create_instr_break(instructor, gap_start, gap_end, priority, added_constraints):
    priority = get_priority_value(priority)
    is_mandatory = False
    if priority == 0:
        is_mandatory = True

    instructor = pull_instructor_obj(instructor)
    constraint_name = "{0}_break_{1}_{2}".format(instructor, gap_start, gap_end)
    
    if okay_to_add_constraint(constraint_name) == False: return

    globs.mainScheduler.add_constraint(constraint_name,
                                       priority,
                                       constraint.instructor_break_constraint,
                                       [    instructor,
                                            gap_start,
                                            gap_end,
                                            is_mandatory ]
                                       )
    added_constraints.add_constraint_listbox(constraint_name, priority)
    return


def get_description_constraint(constraint_type):

    description = ""

    if constraint_type == TYPE_MANUAL_CONCURRENCY:
        description = "Courses that shouldn't be scheduled in the same time:"
    elif constraint_type == TYPE_TIME_COURSE:
        description = "Course should be held in time:\n"
    elif constraint_type == TYPE_DAY_COURSE:
        description = "Course should be held on day(s):\n"
    elif constraint_type == TYPE_ROOM_COURSE:
        description = "Course should be held in one of the following rooms:\n"
    elif constraint_type == TYPE_COMPUTER_PREFERENCE:
        description = "Instructor would prefer to teach classes not requiring computers in a computer lab:\n"
    elif constraint_type == TYPE_DAY:
        description = "Day(s) instructor prefers to teach:\n"
    elif constraint_type == TYPE_INSTRUCTOR_BREAK:
        description = "Instructor would like no classes between:\n"
    elif constraint_type == TYPE_MAX_PER_DAY:
        description = "Maximum class per day instructor prefer to teach:\n"
    elif constraint_type == TYPE_TIME_INSTRUCTOR:
        description = "Time instructor prefers to teach:\n"
    elif constraint_type == TYPE_ROOM_TIME_AVAIL:
        description = "Please select a room:\n"

    return description
