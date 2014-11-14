from __future__ import print_function
import unittest
import random
from genetic import *
import genetic.interface

filename = "tests/schedules/morning_class_test.xml"
sample_scheduler = interface.create_scheduler_from_file_test(filename)
sample_courses = interface.create_course_list_from_file_test(filename)

class TestScheduler(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        sample_scheduler.clear_constraints()

    def test_init(self):
        pass

    def test_clear_constraints(self):
        self.assertEquals(len(sample_scheduler.constraints), 0)
        self.assertEquals(sample_scheduler.max_fitness, 0)
        sample_scheduler.add_constraint("morning_classes", 30, 
                constraint.morning_class, [sample_scheduler.courses[0]]) 
        sample_scheduler.clear_constraints()
        self.assertEquals(len(sample_scheduler.constraints), 0)
        self.assertEquals(sample_scheduler.max_fitness, 0)

    def test_add_contsraint(self):
        sample_scheduler.add_constraint("morning_classes", 30, 
                constraint.morning_class, [sample_scheduler.courses[0]]) 
        sample_scheduler.add_constraint("morning_classes_2", 30, 
                constraint.morning_class, [sample_scheduler.courses[1]]) 
        self.assertEquals(len(sample_scheduler.constraints), 2)
        self.assertEquals(sample_scheduler.max_fitness, 60)

    def test_calc_fitness(self):
        sample_scheduler.add_constraint("lab_on_tr", 30, 
                constraint.lab_on_tr, [sample_scheduler.courses[0]])
        sample_scheduler.calc_fitness(sample_scheduler.weeks[0])
        self.assertEquals(sample_scheduler.weeks[0].fitness, 30)

    def test_find_respective_time_slot(self):
        pass
        """week = sample_scheduler.weeks[0]
        room = week.days[0].rooms[0]
        new_time_slot = scheduler.TimeSlot((10, 00), (11, 00), room)
        time_slot = sample_scheduler.find_respective_time_slot(new_time_slot, week)
        #The two time slots should have the same following attr's:
        self.assertEquals(new_time_slot.start_time, time_slot.start_time)
        self.assertEquals(new_time_slot.end_time, time_slot.end_time)
        self.assertEquals(new_time_slot.day, time_slot.day)
        self.assertEquals(new_time_slot.room, time_slot.room)
        #Make sure not exact same time slot obj"""

    def test_separate_by_credit(self):
        self.assertEquals(len(sample_scheduler.separated[1]), 2)
        self.assertEquals(len(sample_scheduler.separated[3]), 4)
        self.assertEquals(len(sample_scheduler.separated[4]), 1)
        self.assertEquals(sample_scheduler.separated[1][0].code, "CSC 131 001")
        self.assertEquals(sample_scheduler.separated[3][0].code, "CSC 130 002")
        self.assertEquals(sample_scheduler.separated[4][0].code, "CSC 333")

    def test_replace_time_slots(self):
        pass

    def test_assess_inconsistences(self):
        #generic unit tests based on pre defined seeds
        pass

    def test_resolve_inconsistences(self):
        #generic unit tests based on pre defined seeds
        pass

    def test_crossover(self):
        #make sure it produces two schedules
        #everything else is tested in other unit tests
        pass

    def test_inconsistences_integration(self):
        #test that both work together
        pass
    
"""
    def test_generator(self):
        generated = sample_scheduler.generator(sample_scheduler.weeks[0], sample_courses, sample_scheduler.weeks[0].find_empty_time_slots()) 
        if generated.valid == True:
            for each_course in sample_courses:
                check if each_course in generated
                if each_course.pre_schedule:
                    check if each_course.start_time is correct

        if generated.valid == False:
            check that there is at least one course missing or a course is schedule twice or ...
        
    def test_breed(self):
        output size == input + (n choose 2)

    def test_mutate(self):
        given week with no empty slots returns week
"""

if __name__ == "__main__":
    unittest.main()
