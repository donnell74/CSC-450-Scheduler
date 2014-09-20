from __future__ import print_function
from scheduler import *
from structures import *

import unittest
import logging


def init_logging():
    logging.basicConfig(filename='genetic.log', level=logging.DEBUG)
    logging.debug("Logging is initialized")


def main():
    init_logging()
    courses = [Course('CSC333', 4), Course('MTH260', 5), Course('CSC325', 3)]
    rooms = ["CHEK212", "CHEK105"]
    s = Scheduler(courses, rooms)
    s.randomly_fill_schedules()
    s.add_constraint("morning_classes", 30, morning_class, s.courses[0]) 
    s.add_constraint("morning_classes", 30, morning_class, s.courses[1]) 
    s.add_constraint("morning_classes", 30, morning_class, s.courses[2]) 
    #print(s.week)
    s.evolution_loop()
    for w in s.weeks:
      s.calc_fitness(w)
      print(w, "\n")
      print(w.fitness)


if __name__ == "__main__":
    main()
