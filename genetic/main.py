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
    courses = [Course('CSC325', 3), Course('CSC130', 3), Course('CSC131', 3), Course('CSC450', 3), Course('CSC232', 3)]
    rooms = ["CHEK212"]
    s = Scheduler(courses, rooms)
    #print(s.week)
    print(s.weeks[0])


if __name__ == "__main__":
    main()
