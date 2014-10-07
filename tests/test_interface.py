from __future__ import print_function
import unittest
import random
from genetic import *

scheduler = scheduler.create_scheduler_from_file("tests/schedules/morning_class_test.xml")

class TestInterface(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_export_schedules(self):
        #test there is 5 files with schedule_*.py
        #test that file 2 is empty
        pass

if __name__ == "__main__":
    unittest.main()
