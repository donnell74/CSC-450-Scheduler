from __future__ import print_function
from scheduler import *
from structures import *
from interface import *

import unittest
import logging
import interface #


def init_logging():
    logging.basicConfig(filename='genetic.log', level=logging.DEBUG)
    logging.debug("Logging is initialized")


def main():
    init_logging()
    input = open("seeds/scheduler.csv")
    courses_and_details = interface.csv_dict_reader(input)
    instructors = interface.get_instructors(courses_and_details)
    courses_credits_and_instructors = \
        interface.include_instructors_in_dict(courses_and_details, instructors)
    courses = interface.get_courses(courses_credits_and_instructors)
    for instructor in instructors:
        instructor.print_full()
    
    print("Scheduling the following courses:")
    for course in courses:
        print(course)
    rooms = ["CHEK212", "CHEK105", "CHEK213"]
    #time_slots_mwf = ['08:00-08:50', '09:05-09:55', '10:10-11:00', '11:15-12:05', '12:20-13:10', '13:25-14:15', '14:30-15:20', '15:35-16:25']
    #time_slots_tr = ['08:00-09:15', '09:30-10:45', '11:00-12:15', '12:30-13:45', '14:00-15:15', '15:30-16:45']
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    #instructors = ['Shade', 'Wang', 'Liu', 'Vollmar', 'Saquer', 'Smith']
    time_slot_divide = 2

    #print("\nThe following rooms are available: CHEK 212, CHEK105")
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
    export_schedules(s.weeks)
    end = raw_input("Press enter to exit")


if __name__ == "__main__":
    main()
