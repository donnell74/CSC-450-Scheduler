from __future__ import print_function
import structures


class Instructor:

    def __init__(self, name):
        self.name = name
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)

    def print_full(self):
        print(self.name + "\n" + "\n".join([str(c) for c in self.courses]))

    def __eq__(self, other):
        if other == None:
            return False

        return self.name == other.name

    def __str__(self):
        return self.name
