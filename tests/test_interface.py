from __future__ import print_function
import unittest
import random
from genetic import *
from genetic.structures import *

scheduler = interface.create_scheduler_from_file_test("tests/schedules/morning_class_test.xml")

class TestInterface(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_export_schedules(self):
        #test there is 5 files with schedule_*.py
        #test that file 2 is empty
        pass

    def test_default_constraints(self):
        default_scheduler = interface.create_scheduler_from_file_test("tests/schedules/default_constraint_input.xml")
        instructors = [structures.Instructor(name = x) for x in ["Shade", "Saquer", "Liu"] ]
        interface.create_constraints_from_yaml("tests/schedules/test_default_constraints.yaml",
                                     default_scheduler, instructors)
        
        # all default constraints are valid, should be 4 - A CONSTRAINT IS BEING DROPPED, ONLY 3 VALID
        self.assertEquals(len(default_scheduler.constraints), 3)
        
        bad_scheduler = interface.create_scheduler_from_file_test("tests/schedules/default_constraint_input.xml")
        interface.create_constraints_from_yaml("tests/schedules/test_default_constraints_bad.yaml",
                                     bad_scheduler, instructors)
        # one constraint is bad and should be thrown out, should be 2
        self.assertEquals(len(bad_scheduler.constraints), 2)
        
if __name__ == "__main__":
    unittest.main()
