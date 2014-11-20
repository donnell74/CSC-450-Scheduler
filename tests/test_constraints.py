from __future__ import print_function
import unittest
import random
from genetic import *
from genetic.structures import *

sample_scheduler = interface.create_scheduler_from_file_test("tests/schedules/morning_class_test.xml")

class TestConstraints(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        sample_scheduler.clear_constraints()

    def test_max_course(self):
        bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/max_courses_test_fail.xml")
        saquer_instr = structures.Instructor(name="Saquer")

        bad_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                     constraint.instructor_max_courses,
                                     [saquer_instr, 2, False])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        # This schedule should not pass, fitness should be 0
        self.assertEquals(bad_scheduler.weeks[0].fitness, 0)

        good_scheduler = interface.create_scheduler_from_file_test("tests/schedules/max_courses_test_pass.xml")
        good_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                      constraint.instructor_max_courses,
                                      [saquer_instr, 2, False])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        # This schedule should pass, fitness should be 30
        self.assertEquals(good_scheduler.weeks[0].fitness, 30)



if __name__ == "__main__":
    unittest.main()
