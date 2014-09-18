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
    courses = [Course('CSC325', 3)]
    rooms = [Room("CHEK212")]
    s = Scheduler(courses, rooms)
    print(s.week)


if __name__ == "__main__":
    main()
