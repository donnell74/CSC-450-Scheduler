from Tkinter import Frame, Label, Button
from Tkconstants import TOP, RIGHT, LEFT, NW, NE
from guiConstraintsView import ConstraintsView
from guiConstraintsInstructor import InstructorConstraint
from guiConstraintsCourse import CourseConstraint
import globs
from genetic import constraint

class ConstraintPage(Frame):
    """Main constraint frame"""

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Constraint Page", \
                                font =('Helvetica', 18))
        self.head_label.pack()

        self.button_course = Button(self, text="Add Course Constraint",\
                                     command=self.show_course_options)
        self.button_course.pack(anchor = NW, padx = 50, pady = 10)

        self.button_instructor = Button(self, text="Add Instructor Constraint",\
                                         command=self.show_instructor_options)
        self.button_instructor.pack(anchor = NW, padx = 50)

        self.pack(side = TOP, fill = "both")

        # CONTENT
        self.content_container = Frame(self, width="400", height="300")
        self.content_container.pack(fill="both")

        # PAGES
        self.home_page = HomeConstraint(self.content_container)

        self.home_page.pack(anchor = NW, padx = 50)

        self.constraints_view = ConstraintsView(self.content_container)
        self.constraints_view.pack(side = RIGHT, anchor = NE, padx = 50)

        self.instructor_page = InstructorConstraint(self.content_container, self.constraints_view)
        self.course_page = CourseConstraint(self.content_container, self.constraints_view)

        # INITIALIZE WITH HOME PAGE
        self.home_page.lift()

    def show_instructor_options(self):
        """Shows instructor options"""
        self.instructor_page.pack(side = LEFT, padx = 50)
        self.course_page.pack_forget()

    def show_course_options(self):
        """Shows course options"""
        self.course_page.pack(side = LEFT, padx = 50)
        self.instructor_page.pack_forget()

class HomeConstraint(Frame):
    """Default constraint frame"""
    def __init__(self, root):
        Frame.__init__(self, root)

        paragraph_text = " Select an option\n"
        self.description_label = Label(self, text=paragraph_text)
        self.description_label.pack()