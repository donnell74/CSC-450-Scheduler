from __future__ import print_function
import unittest
from genetic.structures import *
from genetic import *

sample_scheduler = interface.create_scheduler_from_file_test("tests/schedules/morning_class_test.xml")

class TestRoom(unittest.TestCase):

    def setUp(self):
        self.room = sample_scheduler.weeks[0].days[0].rooms[0] 

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(len(self.room.schedule), 2)

    def test_info(self):
        self.assertEqual(self.room.info("Day"), sample_scheduler.weeks[0].days[0])
        self.assertEqual(self.room.info("Week"), sample_scheduler.weeks[0])
        self.assertEqual(self.room.info("Schedule"), sample_scheduler) 


if __name__ == "__main__":
    unittest.main()
