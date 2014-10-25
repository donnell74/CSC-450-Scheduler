from __future__ import print_function
import unittest
from genetic.structures import *
from genetic import *

sample_scheduler = interface.create_scheduler_from_file("tests/schedules/morning_class_test.xml")

class TestWeek(unittest.TestCase):

    def setUp(self):
        self.week = sample_scheduler.weeks[0] 

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(len(self.week.days), 5)

    def test_info(self):
        self.assertEqual(self.week.info("Schedule"), sample_scheduler)

    def test_find_course(self):
        self.assertEqual(len(self.week.find_course(sample_scheduler.courses[0])), 3)
        self.assertEqual(len(self.week.find_course(Course("BIO123", "4", "Some Guy"))), 0)

    def test_list_time_slots(self):
        self.assertEqual(len(self.week.list_time_slots()), 13)

    def test_find_empty_time_slots(self):
        self.assertEqual(len(self.week.find_empty_time_slots()), 4)
        self.assertEqual(len(filter(lambda x: x != None, [slot.course for slot in self.week.find_empty_time_slots()])), 0)


if __name__ == "__main__":
    unittest.main()
