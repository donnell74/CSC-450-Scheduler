from __future__ import print_function
from random import randint
from structures import *
from datetime import time, timedelta

import logging


def morning_class(course, scheduler):
    holds = scheduler.week.find_course(course).start_time < time(12, 0) 
    return 1 if holds else 0


known_funcs = {"morning_class", morning_class}

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

    def get_fitness(self, scheduler):
        if self.course == None:
            return func(scheduler) * self.weight
        else:
            return func(self.course, scheduler) * self.weight


class Scheduler:
    """Schedules all courses for a week"""
    def __init__(self, courses, rooms):
        logging.debug("Scheduler init")
        if type(courses) is list:
            if not isinstance(courses[0], Course):
                logging.error("Courses is not a list of Course objects")
                print("Courses is not a list of Course objects")
                return
        else:
            logging.error("Courses is not a list")
            print("Courses is not a list")
            return

        if type(rooms) is not list:
            logging.error("Rooms is not a list")
            print("Rooms is not a list")
            return

        self.week = Week(rooms)
        self.constraints = []
        
        #Number of courses
        self.num_courses = len(courses)
        #Courses grouped by credit hours
#self.courses_by_credits = self.separate_by_credit(courses)
        #Number of groups of credits
        #self.num_credits = len(courses_by_credits.keys())
        #Number of courses grouped by credit hours
        #self.num_course_by_credits = dict(zip(self.courses_by_credits.keys(), #len of values


    def separate_by_credit(self, courses):
        """Groups the courses based on number of credit hours.
        IN: list of course objects
        OUT: dictionary with keys=credit hours and values=list of course objects"""
        courses_by_credits = {}
        for each_course in courses:
            #Case 1: New key-value pair (make new list)
            if each_course.credit not in courses_by_credits.keys():
                courses_by_credits[each_course.credit] = [each_course]
            #Case 2: Add to value's list for key
            else:
                courses_by_credits[each_course.credit].append(each_course)
        return courses_by_credits


    def add_constraint(self, name, weight, func):
        self.constraints.append(Constraint(self, name, weight, func)) 
    

    def calc_fitness(self):
        """Calculates the fitness score of a schedule"""
        total_fitness = 0
        for each_constraint in self.constraints:
            total_fitness += each_constraint.get_fitness(self)

        #do something with fitness score


    def mutate(self, func):
        """Mutates a schedule given an approiate function"""
        if not hasattr(func, '__call__'):
            logging.error("Func passed is not a function")
            print("Func passed is not a function")
        

    def crossover(self, P1, P2):
        """Performs a series of swaps on two schedules to produce children
        IN: 2 parent schedules, P1 and P2
        OUT: 2 children schedules, C1 and C2"""
        #Random number of swaps
        num_swaps = randint(1, self.num_courses)
        for swap in range(num_swaps):
            #Random credit hours selected
            credit = self.courses_by_credits[randint(1, self.num_credits)]
            #todo: perform the counts earlier
#course_a = self.courses_by_credits[credit][randint(1,
#                self.num_course_by_credits[credit])]
            #perform the actual swap
        #todo: 'assign' function, schedule class/week class hookup
    

    def breed(self):
        """Produces a set of schedules based of the current set of schedules"""
        pass


    def evolution_loop(self):
        """Main loop of scheduler, run to evolve towards a high fitness score"""
        pass

