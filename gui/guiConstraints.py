from Tkinter import *
from guiClasses import *
from datetime import time
import sys
sys.path.append("../")
import globs
from genetic import constraint


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
 
    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Instructor Form")
        self.head_label.pack()

        instructor_name = Label(self, text = "Instructor name:")
        instructor_name.pack(side = TOP)

        self.str_instr_name_default = StringVar(self)
        list_of_instructors = globs.instructors
        # list_of_instructors.append("All") # necessary?
        self.str_instr_name_default.set(list_of_instructors[0])
        self.option_instructors = OptionMenu(self, self.str_instr_name_default, *list_of_instructors)
        self.option_instructors.pack(side = TOP)

        # time or day
        label_time_day = Label(self, text = "Type: ")
        label_time_day.pack(side = TOP)
        self.time_day_default.set("Day")
        self.time_day_list = ["Day", "Time"]
        self.option_time_day = OptionMenu(self, self.time_day_default, \
                                          *self.time_day_list)

        # dynamically change dropdowns based on time/day being selected

        # time
        self.label_when = Label(self, text = "When:")
        self.label_when.pack(side = TOP)
        
        self.when_default.set("Before")
        self.when_options = ["Before", "After"]
        self.when_menu = OptionMenu(self, self.when_default, *self.when_options)
        self.when_menu.pack(side = TOP)

        # day
        self.label_day = Label(self, text = "Day(s):")
        self.label_day.pack(side = TOP)

        self.day_menu_default.set("MWF")
        self.day_menu_list = ["MWF", "TR"]  # pull this from globs?
        self.day_menu = OptionMenu(self, self.day_menu_default, \
                                   *self.day_menu_list)
        

class CourseConstraint(Page):
 
    def __init__(self, root):
        Frame.__init__(self, root)
#         self.head_label = Label(self, text="Course Form")
#         self.head_label.pack()
#

        globs.init()
        
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
        
        self.str_priority_default = StringVar(self)
        self.str_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self, self.str_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack(side = TOP)
        
        self.button_go = Button(self, text="Add Constraint", command=self.go)
        self.button_go.pack(side = RIGHT)
        
    def go(self):
        course = self.str_course_default.get()
        time =  self.str_time_default.get()
        when = self.str_when_default.get()
        priority = self.str_priority_default.get()
        createConstraint(course, time, when, priority)
    
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
        
class ConstraintPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Constraint Page", \
                                font =('Helvetica', 18))
        self.head_label.pack()
        self.create_widgets()
        self.pack(side = TOP, fill = "both")

        
        # CONTENT
        self.content_container = Frame(self, width="400", height="300")
        self.content_container.pack(side=LEFT, fill="both")
        
        # PAGES
        self.home_page = HomeConstraintPage(self.content_container)
        self.home_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        
        self.instructor_page = InstructorConstraint(self.content_container)
        self.instructor_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        
        self.course_page = CourseConstraint(self.content_container)
        self.course_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        
        # INITIALIZE WITH HOME PAGE
        self.home_page.lift()
        
    def add_instructor_constraint(self):
        self.instructor_page.lift()
        
    def add_course_constraint(self):
        self.course_page.lift()
        
    def create_widgets(self):
        
        self.button_course = Button(self, text="Add Course Constraint", command=self.add_course_constraint)
        self.button_course.pack(side = TOP)

        self.button_instructor = Button(self, text="Add Instructor Constraint", command=self.add_instructor_constraint)
        self.button_instructor.pack(side = TOP)
        
def createConstraint(course, start_time, when, priority):
    # convert the priority string to a weight value for fitness score
    if priority == "Low":
        priority = 10
    elif priority == "Medium":
        priority = 25
    elif priority == "High":
        priority = 50
    else:  # priority should be mandatory
        priority = 100
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
    return 
    
