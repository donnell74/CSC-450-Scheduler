import unittest
from gui import *
class TestGuiConstraint(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_get_priority_value(self):
        self.assertEqual(guiConstraints.get_priority_value("Low"), 10)


if __name__ == "__main__":
    unittest.main()