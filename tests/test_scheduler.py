from __future__ import print_function
import unittest
import random
from genetic import *

sample_scheduler = scheduler.create_scheduler_from_file("test/schedules/morning_class_test.xml")
sample_courses = scheduler.create_course_list_from_file("test/schedules/morning_class_test.xml")

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
        sample_scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [sample_scheduler.courses[0]]) 
        sample_scheduler.clear_constraints()
        self.assertEquals(len(sample_scheduler.constraints), 0)
        self.assertEquals(sample_scheduler.max_fitness, 0)

    def test_add_contsraint(self):
        sample_scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [sample_scheduler.courses[0]]) 
        sample_scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [sample_scheduler.courses[1]]) 
        self.assertEquals(len(sample_scheduler.constraints), 2)
        self.assertEquals(sample_scheduler.max_fitness, 60)

    def test_calc_fitness(self):
        sample_scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [sample_scheduler.courses[0]]) 
        sample_scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [sample_scheduler.courses[1]]) 
        sample_scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [sample_scheduler.courses[2]]) 
        sample_scheduler.calc_fitness(sample_scheduler.weeks[0])
        self.assertEquals(sample_scheduler.weeks[0].fitness, 60)

    def test_separate_by_credit(self):
        separated_by_credits = sample_scheduler.separate_by_credit(sample_courses)
        self.assertEquals(separated_by_credits, {'3': sample_courses})

    def test_find_respective_time_slot(self):
        week = sample_scheduler.weeks[0]
        room = week.days[0].rooms[0]
        new_time_slot = scheduler.TimeSlot((10, 00), (11, 00), room)
        time_slot = sample_scheduler.find_respective_time_slot(new_time_slot, week)
        #The two time slots should have the same following attr's:
        self.assertEquals(new_time_slot.start_time, time_slot.start_time)
        self.assertEquals(new_time_slot.end_time, time_slot.end_time)
        self.assertEquals(new_time_slot.day, time_slot.day)
        self.assertEquals(new_time_slot.room, time_slot.room)
        #Make sure not exact same time slot obj

    
        

    def test_separate_by_credit(self):
        self.assertEquals(len(scheduler.separated["1"]), 0)
        self.assertEquals(len(scheduler.separated["3"]), 1)
        self.assertEquals(len(scheduler.separated["4"]), 1)
        self.assertEquals(len(scheduler.separated["5"]), 1)
        self.assertEquals(scheduler.separated["3"][0].code, "CSC130")
        self.assertEquals(scheduler.separated["4"][0].code, "CSC131")
        self.assertEquals(scheduler.separated["5"][0].code, "CSC232")


if __name__ == "__main__":
    unittest.main()
