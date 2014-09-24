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
    print("Scheduling the following courses: CSC325 (3), CSC232 (3), CSC450 (3), CSC333(4)")
    courses = [Course('CSC325', 3), Course('CSC232', 3), Course('CSC450', 3), Course('CSC333', 4)]
    rooms = ["CHEK212", "CHEK105"]
    #time_slots_mwf = ['08:00-08:50', '09:05-09:55', '10:10-11:00', '11:15-12:05', '12:20-13:10', '13:25-14:15', '14:30-15:20', '15:35-16:25']
    #time_slots_tr = ['08:00-09:15', '09:30-10:45', '11:00-12:15', '12:30-13:45', '14:00-15:15', '15:30-16:45']
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    time_slot_divide = 2

    print("\nThe following rooms are available: CHEK 212, CHEK105")
    print("\nThe time slots are 09:00-10:00, 10:00-11:00, 11:00-12:00, 12:00-13:00")
    print("\nThe constraints are that no classes can be scheduled in the same place at the",
          "same time, and that all the classes but CSC333 prefer to be scheduled with a",
          "start time before 12") 
    begin = raw_input("\nPress enter to schedule")

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
      print("Fitness level:", w.fitness)
    end = raw_input("Press enter to exit")


if __name__ == "__main__":
    main()
