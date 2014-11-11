from __future__ import print_function
import unittest
import random
from genetic import *

scheduler = interface.create_scheduler_from_file("tests/schedules/morning_class_test.xml")

class TestConstraints(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        scheduler.clear_constraints()

if __name__ == "__main__":
    unittest.main()
