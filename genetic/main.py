from __future__ import print_function
from scheduler import Scheduler
from structures import *

import unittest
import logging


def init_logging():
    logging.basicConfig(filename='genetic.log', level=logging.DEBUG)
    logging.debug("Logging is initialized")


def main():
    init_logging()
    courses = [Course('CSC333', 4), Course('MTH260', 5), Course('CSC325', 3)]
    rooms = ["CHEK212", "CHEK105"]
    s = Scheduler(courses, rooms)
    s.randomly_fill_schedules()
    #print(s.week)
    print(s.weeks[0])


if __name__ == "__main__":
    main()
