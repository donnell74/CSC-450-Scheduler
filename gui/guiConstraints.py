from Tkinter import *
from guiClasses import *
from datetime import time
import sys
sys.path.append("../")
import globs
from genetic import constraint
from ScrolledText import ScrolledText  # textbox with scrollbar for view screen


class Page(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
 
    def show(self):
        self.lift()

class AddedConstraintsScreen(Page):
    def __init__(self, root, constraints):
        Frame.__init__(self, root, width = 30, height = 50)
        
        # list that holds Constraint objects
        self.constraints = constraints

        # holds the scrollbox output text for the added constraints
        self.added_constraints = []
        
        textL = " Constraints Added: "
        self.text = Label(self, text = textL)
        self.text.pack(anchor = NW, expand = YES)
        
        # scrollbox
        self.scroll = ScrolledText(self, undo = True, width = 40, height = 15)
        self.scroll['font'] = ('Courier New', '11')
        self.scroll.pack(fill = BOTH, padx = 5, pady = 5)
        
    def view_constraints(self, text):
        output = text[0]
        if text[1] == 10:
            output += 'Low'
        elif text[1] == 25:
            output += 'Medium'
        elif text[1] == 50:
            output += 'High'
        elif text[1] == 100:
            output += 'Mandatory'

        output += '\n'
        self.added_constraints.append(output)

        self.scroll.delete('1.0', END)
        for i in xrange(len(self.constraints)):
            self.scroll.insert(INSERT, self.added_constraints[i])
        
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
        self.time_day_list = ["Time", "Day"]
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

        self.time_slot_menu = OptionMenu(self.time_frame, self.time_default, *self.time_slots[1:]) # default is before so knock out the first slot to avoid invalid constraints
        self.time_slot_menu.pack(side = TOP)

        self.priority_label = Label(self.time_frame, text = "Priority: ")
        self.priority_label.pack()
        self.instr_time_priority_default = StringVar(self)
        self.instr_time_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self.time_frame, self.instr_time_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)

        self.submit_time = Button(self.time_frame, text = "Add Constraint", command = self.add_instr_time)
        self.submit_time.pack(side = RIGHT, pady = 25)

        # day - CHECKBOXES
        self.day_frame = Frame(self, width = 100)  # don't pack this because Time is the default option so days shouldn't be visible
                        
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
        self.option_priority = OptionMenu(self.day_frame, self.instr_day_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)
        

        self.submit_day = Button(self.day_frame, text = "Add Constraint", command = self.add_instr_day)
        self.submit_day.pack(side = TOP, pady = 25)



        

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
            self.day_frame.pack()
        else:
            self.time_frame.pack()
            self.day_frame.pack_forget()

        
    

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
        self.option_priority = OptionMenu(self, self.course_time_priority_default, "Low", "Medium", "High", "Mandatory")
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

        self.added_constraints = AddedConstraintsScreen(self.content_container, constraints)
        #self.added_constraints.place(in_ = self.instructor_page, anchor = E)
        #self.added_constraints.place(in_ = self.course_page, anchor = E)
        self.added_constraints.pack(side = RIGHT, anchor = NE, padx = 50)
        
        self.instructor_page = InstructorConstraint(self.content_container, self.added_constraints)
        #self.instructor_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        #self.instructor_page.pack(side = LEFT)
        
        self.course_page = CourseConstraint(self.content_container, self.added_constraints)
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
    else:  # priority should be mandatory
        priority = 100
    return priority


def pull_instructor_obj(instructor):
    for i in range(len(globs.instructors)):
        if instructor == globs.instructors[i].name:  # look for appropriate instructor object
            instructor = globs.instructors[i]
            break
    return instructor

def create_course_time_constraint(course, start_time, when, priority, added_constraints):
    # convert the priority string to a weight value for fitness score
    priority = get_priority_value(priority)
    constraint_name = "{0}_{1}_{2}".format(course, when, start_time)
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
                                                 [course, time_obj]) 
        else:  # one course AFTER a time
             globs.mainScheduler.add_constraint(constraint_name, priority,
                                        constraint.course_after_time,
                                         [course, time_obj]) 
    else: # applies to all courses
        course = globs.mainScheduler.courses
        if when == "Before":
             globs.mainScheduler.add_constraint(constraint_name, priority,
                                                constraint.all_before_time,
                                                 [course, time_obj]) 
        else: # all courses AFTER
             globs.mainScheduler.add_constraint(constraint_name, priority,
                                                constraint.all_after_time,
                                                 [course, time_obj]) 
    print "Added constraint ", constraint_name, "with priority/weight = ", str(priority)

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return 
    

def create_time_pref_constraint(instructor, before_after, timeslot, priority, added_constraints):
    priority = get_priority_value(priority)
    instructor = pull_instructor_obj(instructor)
    hour, minute = timeslot.split(":")
    time_obj = time( int(hour), int(minute) )
    constraint_name = "{0}_prefers_{1}_{2}".format(instructor.name, before_after.lower(), str(time_obj))
    #print(constraint_name, "weight = " + str(priority))
    
    if before_after == "Before":
        globs.mainScheduler.add_constraint(constraint_name, priority,  \
                                           constraint.instructor_time_pref_before, [instructor, timeslot])
        
    else:  # after a time
        globs.mainScheduler.add_constraint(constraint_name, priority, \
                                           constraint.instructor_time_pref_after, [instructor, timeslot])
        pass
    
    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return


def create_day_pref_constraint(instructor, day_code, priority, added_constraints):
    priority = get_priority_value(priority)
    instructor = pull_instructor_obj(instructor)
    if len(day_code) > 4:  # can't select every day of the week, bad constraint
        print("Error, a day preference can't be all days of the week, try again.")
        return # return False?  Or, the error mesage
    constraint_name = "{0}_prefers_{1}".format(instructor.name, day_code)
    
    day_code = day_code.lower()    
    globs.mainScheduler.add_constraint(constraint_name, priority, constraint.instructor_preference_day, [instructor, day_code])

    # update scrollbox with this created constraint
    added_constraints.view_constraints((constraint_name + " Priority = ", priority))
    return

