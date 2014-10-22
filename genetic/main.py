from __future__ import print_function
from scheduler import *
from structures import *

import unittest
import interface
import globs

def main():
    '''input = open("seeds/Scheduler.csv")
    courses_and_details = interface.csv_dict_reader(input)
    instructors = interface.get_instructors(courses_and_details)
    courses_credits_and_instructors = \
        interface.include_instructors_in_dict(courses_and_details, instructors)
    courses = interface.get_courses(courses_credits_and_instructors)'''
    instructors = globs.instructors
    courses = globs.courses
    time_slots = globs.time_slots
    rooms = globs.rooms
    course_titles = globs.course_titles
    time_slot_divide = globs.time_slot_divide

    for instructor in instructors:
        instructor.print_full()
        print()
    print()

    print("Scheduling the following courses:")
    for course in courses:
        print(course)
    #time_slots_mwf = ['08:00-08:50', '09:05-09:55', '10:10-11:00', '11:15-12:05', '12:20-13:10', '13:25-14:15', '14:30-15:20', '15:35-16:25']
    #time_slots_tr = ['08:00-09:15', '09:30-10:45', '11:00-12:15', '12:30-13:45', '14:00-15:15', '15:30-16:45']
    #time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    #instructors = ['Shade', 'Wang', 'Liu', 'Vollmar', 'Saquer', 'Smith']
    #time_slot_divide = 2


    #begin = raw_input("\nPress enter to schedule")

    s = Scheduler(courses, rooms, time_slots, time_slot_divide)
    s.generate_starting_population()
    #s.add_constraint("morning_classes", 30, morning_class, s.courses[0])
    #s.add_constraint("morning_classes", 30, morning_class, s.courses[1])
    #s.add_constraint("morning_classes", 30, morning_class, s.courses[2])
    #s.add_constraint("morning_classes", 30, morning_class, s.courses[3])

    #s.add_constraint("all_before_noon", 30, all_before_time, s.courses, time(12,0))
    #s.add_constraint("all_after_nine", 30, all_after_time, s.courses, time(9,0))
    #s.add_constraint("232_after_10", 30, course_after_time, s.courses[1], time(10,0))
    #s.add_constraint("325_before_10", 30, course_before_time, s.courses[0], time(10,0))
    s.add_constraint("morning_classes", 30, morning_class, [s.courses[0]])
    s.add_constraint("morning_classes", 30, morning_class, [s.courses[1]])
    s.add_constraint("morning_classes", 30, morning_class, [s.courses[2]])
    s.add_constraint("instructor conflict", 0, instructor_conflict, instructors)
    s.add_constraint("sequential_time_different_building_conflict", 0, sequential_time_different_building_conflict, instructors)
    s.add_constraint("subsequent courses", 0, num_subsequent_courses, instructors)

    s.evolution_loop()
    interface.export_schedules(s.weeks)

    end = raw_input("Press enter to exit")


if __name__ == "__main__":
    main()
