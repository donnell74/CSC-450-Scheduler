from structures import *
from datetime import time, timedelta

def morning_class(this_week, args):
    #Find course returns a list of time slots, but they should all be at the same time
    holds = False
    if isinstance(args[0], Course):
        holds = this_week.find_course(args[0])[0].start_time < time(12, 0)

    return 1 if holds else 0


def instructor_conflict(this_week, instructors):
    """
    Checks for instructors teaching multiple courses at once.  If none are found,
    passes; else, fails.
    Note: Currently based purely off start time due to MWF-only timeslot system.
    Todo: Check type of args
    IN: list of all instructor objects
    OUT: 0/1 for "holds"
    """
    for each_instructor in instructors:
        times = []
        count = 0
        for each_instructors_course in each_instructor.courses:
            times.append(this_week.find_course(each_instructors_course)[0].start_time)
        while len(times) > 0:
            each_time = times.pop(0)
            for each_other_time in times:
                if each_time == each_other_time:
                    count += 1
        
        if count > 0:
            this_week.valid = False
    return 0 


class Constraint:
    def __init__(self, name, weight, func, args = []):
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

        self.name = name
        self.weight = weight
        self.args = args
        if type(func) is str:
            self.func = func
        else:
            self.func = func

    def get_fitness(self, this_week):
        return self.func(this_week, self.args) * self.weight


