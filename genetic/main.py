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
    #time_slots_mwf = ['08:00-08:50', '09:05-09:55', '10:10-11:00', '11:15-12:05', '12:20-13:10', '13:25-14:15', '14:30-15:20', '15:35-16:25']
    #time_slots_tr = ['08:00-09:15', '09:30-10:45', '11:00-12:15', '12:30-13:45', '14:00-15:15', '15:30-16:45']
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    time_slot_divide = 2

    s = Scheduler(courses, rooms, time_slots, time_slot_divide)
    s.generate_starting_population()
    #for week in s.weeks:
    #    print(week)
    s.add_constraint("morning_classes", 30, morning_class, s.courses[0]) 
    s.add_constraint("morning_classes", 30, morning_class, s.courses[1]) 
    s.add_constraint("morning_classes", 30, morning_class, s.courses[2]) 

    s.evolution_loop()
    for w in s.weeks:
      s.calc_fitness(w)
      print(w, "\n**************************************\n")
      print(w.fitness)


if __name__ == "__main__":
    main()
