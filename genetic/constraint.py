from structures import Course
from datetime import time, timedelta

def morning_class(course, this_week):
    #Find course returns a list of time slots, but they should all be at the same time
    holds = this_week.find_course(course)[0].start_time < time(12, 0)
    return 1 if holds else 0


class Constraint:
    def __init__(self, name, weight, func, course = None):
        if type(name) is not str:
            logging.error("Name is not a string")
            print("Name is not a string")
            return
        
        if type(weight) is not int:
            logging.error("Weight is not a string")
            print("Weight is not a string")
            return

        if not hasattr(func, '__call__'):
            if type(func) is str and not known_funcs.has_key(func):
                logging.error("Func string passed is not known")
                print("Func string passed is not known")
                return
            else:
                logging.error("Func passed is not a function")
                print("Func passed is not a function")
                return

        if not isinstance(course, Course):
            logging.error("Course is not of object type course")
            print("Course is not of object type course")
            return

        self.name = name
        self.weight = weight
        self.course = course
        if type(func) is str:
            self.func = func
        else:
            self.func = func

    def get_fitness(self, this_week):
        if self.course == None:
            return self.func(this_week) * self.weight
        else:
            return self.func(self.course, this_week) * self.weight


