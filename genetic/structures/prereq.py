import structures

class Prereq:
    """ Represents the prerequisites for a single course """
    def __init__(self, absolute_course, list_of_all_courses):
        self.absolute_course = absolute_course # E.g.: 'CSC150'
        self.absolute_prereqs = [] # list of absolute course strings
        self.prereqs = [] # list of course objects as prereqs
        self.courses = self.determine_courses(list_of_all_courses) # course objects of absolute course

    def add_prereq(self, absolute_course, list_of_all_courses):
        """ Adds as prereq for absolute and objects """
        self.absolute_prereqs.append(absolute_course)
        for each_course in list_of_all_courses:
            if each_course.absolute_course == absolute_course:
                self.prereqs.append(each_course)

    def determine_courses(self, courses):
        """
        IN: list of courses
        OUT: list of courses for which absolute_course applies
        """
        course_list = []
        for course in courses:
            if course.absolute_course == self.absolute_course:
                course_list.append(course)
        return course_list

    def __str__(self):
        return self.absolute_course + " requires " + "".join([str(p) + ", " for p in self.absolute_prereqs])
