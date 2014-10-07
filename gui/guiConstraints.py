from Tkinter import *
from guiClasses import *
from datetime import time

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

class CourseConstraint(Page):
 
    def __init__(self, root):
        Frame.__init__(self, root)
#         self.head_label = Label(self, text="Course Form")
#         self.head_label.pack()
#         
        message_course = Label(self, text="Course code:")
        message_course.pack({"side": "top"})

        self.str_course_default = StringVar(self)
        self.str_course_default.set("CSC450") 
        self.option_course = OptionMenu(self, self.str_course_default, "CSC450","CSC333", "CSC232", "CSC325", "all")
        self.option_course.pack({"side": "top"})
        
        message_when = Label(self, text="When:")
        message_when.pack({"side": "top"})
        
        self.str_when_default = StringVar(self)
        self.str_when_default.set("Before")
        self.option_when = OptionMenu(self, self.str_when_default, "Before", "After")
        self.option_when.pack({"side": "top"})
        
        message_time = Label(self, text="Time:")
        message_time.pack({"side": "top"})
        
        self.str_time_default = StringVar(self)
        self.str_time_default.set("09:00")
        self.option_time = OptionMenu(self, self.str_time_default, "09:00", "10:00", "11:00", "12:00")
        self.option_time.pack({"side": "top"})
        
        message_priority = Label(self, text="Priority:")
        message_priority.pack({"side": "top"})
        
        self.str_priority_default = StringVar(self)
        self.str_priority_default.set("Low") # initial value
        self.option_priority = OptionMenu(self, self.str_priority_default, "Low", "Medium", "High", "Mandatory")
        self.option_priority.pack({"side": "top"})
        
        self.button_go = Button(self, text="Add Constraint", command=self.go)
        self.button_go.pack({"side": "right"})
        
    def go(self):
        course = self.str_course_default.get()
        time =  self.str_time_default.get()
        when = self.str_when_default.get()
        priority = self.str_priority_default.get()
        createConstraint(course, time, when, priority)
        
class ConstraintPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Constraint Page")
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
        
        self.button_course = Button(self, text="add course constraint", command=self.add_course_constraint)
        self.button_course.pack(side = TOP)

        self.button_instructor = Button(self, text="add instructor constraint", command=self.add_instructor_constraint)
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

    # MOSTLY PSEUDOCODE, TO BE IMPLEMENTED WHEN GUI AND SCHEDULER ARE LINKED
    # if course != "all":  
        #handle finding the course object in s.courses, assign it to course
        # for c in s.courses:
        #    if c.code == course:
        #        course = c
        # if when == "Before"   
            # s.add_constraint(Constraint(constraint_name, priority, course_before_constraint, this_week, course, time ) )
        # else:  # one course AFTER a time
            # add course_after_constraint(this_week, course, time)
    # else: # applies to all courses
        # if when == "before"
            # add all_before_constraint(this_week, time)
        # else: # all courses AFTER
            # add all_after_constraint(this_week, time)
    print constraint_name, "priority/weight = " + str(priority)
    return 
    
