from __future__ import print_function
import unittest
from genetic.structures import *
from genetic import *

sample_scheduler = interface.create_scheduler_from_file_test("tests/schedules/morning_class_test.xml")

class TestRoom(unittest.TestCase):

    def setUp(self):
        self.roomMWF = sample_scheduler.weeks[0].days[0].rooms[0] 
        self.roomTR = sample_scheduler.weeks[0].days[1].rooms[0] 

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(len(self.roomMWF.schedule), 3)
        self.assertEqual(len(self.roomTR.schedule), 5)


if __name__ == "__main__":
    unittest.main()
