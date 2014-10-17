from __future__ import print_function
import unittest
import random
from genetic import *

scheduler = scheduler.create_scheduler_from_file("tests/schedules/morning_class_test.xml")

class TestScheduler(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        scheduler.clear_constraints()

    def test_init(self):
        pass

    def test_clear_constraints(self):
        self.assertEquals(len(scheduler.constraints), 0)
        self.assertEquals(scheduler.max_fitness, 0)
        scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [scheduler.courses[0]]) 
        scheduler.clear_constraints()
        self.assertEquals(len(scheduler.constraints), 0)
        self.assertEquals(scheduler.max_fitness, 0)

    def test_add_contsraint(self):
        scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [scheduler.courses[0]]) 
        scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [scheduler.courses[1]]) 
        self.assertEquals(len(scheduler.constraints), 2)
        self.assertEquals(scheduler.max_fitness, 60)

    def test_calc_fitness(self):
        scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [scheduler.courses[0]]) 
        scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [scheduler.courses[1]]) 
        scheduler.add_constraint("morning_classes", 30, constraint.morning_class, [scheduler.courses[2]]) 
        scheduler.calc_fitness(scheduler.weeks[0])
        self.assertEquals(scheduler.weeks[0].fitness, 60)

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
