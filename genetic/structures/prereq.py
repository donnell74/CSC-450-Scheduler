import structures

class Prereq:
    def __init__(self, absolute_course, list_of_all_courses):
        #Ex: 'CSC150'
        self.absolute_course = absolute_course
        #list of absolute courses (str's)
        self.absolute_prereqs = []
        #list of course objects as prereqs
        self.prereqs = []
        #course objects for absolute course
        self.courses = self.determine_courses(list_of_all_courses)
 
    def add_prereq(self, absolute_course, list_of_all_courses):
        """Adds as prereq for absolute and objects"""
        self.absolute_prereqs.append(absolute_course)
        for each_course in list_of_all_courses:
            if each_course.absolute_course == absolute_course:
                self.prereqs.append(each_course)

    def determine_courses(self, courses):
        """IN: list of courses
        OUT: list of courses for which absolute_course applies"""
        out = []
        for course in courses:
            if course.absolute_course == self.absolute_course:
                out.append(course)
        return out

    def __str__(self):
        return self.absolute_course
