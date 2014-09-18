from __future__ import print_function
from random import randint
from week import *

import logging

class Scheduler:
    """Schedules all courses for a week"""
    def __init__(self, courses, rooms):
        logging.debug("Scheduler init")
        if type(courses) is list:
            print(type(courses[0]))
            if type(courses[0]) is not Course:
                logging.error("Courses is not a list of Course objects")
                print("Courses is not a list of Course objects")
                return
        else:
            logging.error("Courses is not a list")
            print("Courses is not a list")
            return

        if type(rooms) is list:
            if type(rooms[0]) is not Room:
                logging.error("Rooms is not a list of Room objects")
                print("Rooms is not a list of Room objects")
                return
        else:
            logging.error("Rooms is not a list")
            print("Rooms is not a list")

        self.week = Week()
        
        #Number of courses
        self.num_courses = len(courses)
        #Courses grouped by credit hours
        self.courses_by_credits = separate_by_credit(courses)
        #Number of groups of credits
        self.num_credits = len(courses_by_credits.keys())
        #Number of courses grouped by credit hours
        #self.num_course_by_credits = dict(zip(self.courses_by_credits.keys(), #len of values


    def separate_by_credit(self, courses):
        """Groups the courses based on number of credit hours.
        IN: list of course objects
        OUT: dictionary with keys=credit hours and values=list of course objects"""
        courses_by_credits = {}
        for each course in courses:
            #Case 1: New key-value pair (make new list)
            if course.credit not in courses_by_credits.keys():
                courses_by_credits[course.credit] = [course]
            #Case 2: Add to value's list for key
            else:
                courses_by_credits[course.credit].append(course)
        return courses_by_credits


    def calc_fitness(self):
        """Calculates the fitness score of a schedule"""
        pass


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
            course_a = self.courses_by_credits[credit][randint(1,
                self.num_course_by_credits[credit])]
            #perform the actual swap
        #todo: 'assign' function, schedule class/week class hookup
    

    def breed(self):
        """Produces a set of schedules based of the current set of schedules"""
        pass


    def evolution_loop(self):
        """Main loop of scheduler, run to evolve towards a high fitness score"""
        pass
