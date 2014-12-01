from __future__ import print_function
import unittest
import random
from genetic import *
from genetic.structures import *
from datetime import time

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

    def test_lab_constraint(self):
        sample_scheduler.add_constraint("is lab", 30,
                                        constraint.lab_on_tr,
                                        [sample_scheduler.courses[0]])
        sample_scheduler.calc_fitness(sample_scheduler.weeks[0])
        self.assertEquals(sample_scheduler.weeks[0].fitness, 0)
        sample_scheduler.clear_constraints()
        sample_scheduler.add_constraint("is lab", 30,
                                        constraint.lab_on_tr,
                                        [sample_scheduler.courses[1]])
        sample_scheduler.calc_fitness(sample_scheduler.weeks[0])
        self.assertEquals(sample_scheduler.weeks[0].fitness, 30)

    def test_instructor_time_pref_before(self):
        bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/instructor_time_before_test_fail.xml")
        volmar_instr = structures.Instructor(name="Volmar")
        volmar_instr.courses = [c for c in bad_scheduler.courses if c.code in ("CSC 232 A","CSC 232 001")]
        bad_scheduler.add_constraint("volmar_time_pref_before_12", 30,
                                      constraint.instructor_time_pref_before,
                                      [volmar_instr, time(13, 0), False])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        #This schedule should not pass, fitness should be 30
        self.assertEquals(bad_scheduler.weeks[0].fitness, 30)

        #bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/instructor_time_before_test_fail.xml")
        #bad_time_slot_12 = structures.TimeSlot(start_time="11:00",
        #                                   end_time="12:00",
        #                                   this_room=bad_scheduler.rooms[0])
        
        good_scheduler = interface.create_scheduler_from_file_test("tests/schedules/instructor_time_before_test_pass.xml")
        volmar_instr = structures.Instructor(name="Volmar")
        volmar_instr.courses = [c for c in good_scheduler.courses if c.code in ("CSC 232 A","CSC 232 001")]
        good_scheduler.add_constraint("volmar_time_pref_before_12", 30,
                                      constraint.instructor_time_pref_before,
                                      [volmar_instr, time(13, 0), False])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        #This schedule should pass, fitness should be 30
        self.assertEquals(good_scheduler.weeks[0].fitness, 30)

    def test_instructor_time_pref_after(self):
        bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/instructor_time_after_test_fail.xml")
        volmar_instr = structures.Instructor(name="Volmar")
        volmar_instr.courses = [c for c in bad_scheduler.courses if c.code in ("CSC 232 A","CSC 232 001")]
        bad_scheduler.add_constraint("volmar_time_pref_after_12", 30,
                                      constraint.instructor_time_pref_after,
                                      [volmar_instr, time(13, 0), True])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        #This schedule should not pass, fitness should be 30
        self.assertEquals(bad_scheduler.weeks[0].fitness, 0)

        #bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/instructor_time_before_test_fail.xml")
        #bad_time_slot_12 = structures.TimeSlot(start_time="11:00",
        #                                   end_time="12:00",
        #                                   this_room=bad_scheduler.rooms[0])
        
        good_scheduler = interface.create_scheduler_from_file_test("tests/schedules/instructor_time_after_test_pass.xml")
        volmar_instr = structures.Instructor(name="Volmar")
        volmar_instr.courses = [c for c in good_scheduler.courses if c.code in ("CSC 232 A","CSC 232 001")]
        good_scheduler.add_constraint("volmar_time_pref_after_12", 30,
                                      constraint.instructor_time_pref_after,
                                      [volmar_instr, time(13, 0), True])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        #This schedule should pass, fitness should be 30
        self.assertEquals(good_scheduler.weeks[0].fitness, 0)

    def test_all_before_time(self):
        bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/all_before_time_fail.xml")
        saquer_instr = structures.Instructor(name="Saquer")

        # non mandatory check - bad
        bad_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                     constraint.all_before_time,
                                     [bad_scheduler.courses, time(13, 0), False])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        # This schedule should not pass, fitness should be 0
        self.assertEquals(bad_scheduler.weeks[0].fitness, 0)

        # mandatory check - bad
        bad_scheduler.clear_constraints()
        bad_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                     constraint.all_before_time,
                                     [bad_scheduler.courses, time(13, 0), True])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        # This schedule should not pass, fitness should be 0
        self.assertFalse(bad_scheduler.weeks[0].fitness, 30)

        # non mandatory check - good
        good_scheduler = interface.create_scheduler_from_file_test("tests/schedules/all_before_time_pass.xml")
        good_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                      constraint.all_before_time,
                                      [good_scheduler.courses, time(13, 0), False])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        # This schedule should pass, fitness should be 30
        self.assertEquals(good_scheduler.weeks[0].fitness, 30)

        # mandatory check - good
        good_scheduler.clear_constraints()
        good_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                      constraint.all_before_time,
                                      [good_scheduler.courses, time(13, 0), True])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        # This schedule should pass, fitness should be 30
        self.assertTrue(good_scheduler.weeks[0].valid)


    def test_all_after_time(self):
        bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/all_after_time_fail.xml")
        saquer_instr = structures.Instructor(name="Saquer")

        # non mandatory check - bad
        bad_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                     constraint.all_after_time,
                                     [bad_scheduler.courses, time(11, 0), False])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        # This schedule should not pass, fitness should be 0
        self.assertEquals(bad_scheduler.weeks[0].valid, 0)

        # mandatory check - bad
        bad_scheduler.clear_constraints()
        bad_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                     constraint.all_after_time,
                                     [bad_scheduler.courses, time(13, 0), True])
        bad_scheduler.calc_fitness(bad_scheduler.weeks[0])
        # This schedule should not pass, fitness should be 0
        self.assertFalse(bad_scheduler.weeks[0].valid)

        # non mandatory check - good
        good_scheduler = interface.create_scheduler_from_file_test("tests/schedules/all_after_time_pass.xml")
        good_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                      constraint.all_after_time,
                                      [good_scheduler.courses, time(13, 0), False])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        # This schedule should pass, fitness should be 30
        self.assertEquals(good_scheduler.weeks[0].fitness, 30)

        # mandatory check - good
        good_scheduler.clear_constraints()
        good_scheduler.add_constraint("Saquer_max_courses_2", 30,
                                      constraint.all_after_time,
                                      [bad_scheduler.courses, time(13, 0), True])
        good_scheduler.calc_fitness(good_scheduler.weeks[0])
        # This schedule should pass, fitness should be 30
        self.assertTrue(good_scheduler.weeks[0].valid)
        
        


if __name__ == "__main__":
    unittest.main()
