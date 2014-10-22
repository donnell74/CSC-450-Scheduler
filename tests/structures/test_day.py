from __future__ import print_function
import unittest
from genetic.structures import *
from genetic import *

scheduler = scheduler.create_scheduler_from_file("tests/schedules/morning_class_test.xml")

class TestDay(unittest.TestCase):

    def setUp(self):
        self.day = scheduler.weeks[0].days[0] 

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(len(self.day.rooms), 1)

    def test_info(self):
        self.assertEqual(self.day.info("Week"), scheduler.weeks[0])
        self.assertEqual(self.day.info("Schedule"), scheduler) 


if __name__ == "__main__":
    unittest.main()
