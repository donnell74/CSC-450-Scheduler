from __future__ import print_function
import logging

class Scheduler:
    """Schedules all courses for a week"""
    def __init__(self, courses, rooms):
        logging.debug("Scheduler init")
        if type(courses) is list:
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

    def calc_fitness(self):
        """Calculates the fitness score of a schedule"""
        pass


    def mutate(self, func):
        """Mutates a schedule given an approiate function"""
        if not hasattr(func, '__call__'):
            logging.error("Func passed is not a function")
            print("Func passed is not a function")
        


    def breed(self):
        """Produces a set of schedules based of the current set of schedules"""
        pass


    def evolution_loop(self):
        """Main loop of scheduler, run to evolve towards a high fitness score"""
        pass
