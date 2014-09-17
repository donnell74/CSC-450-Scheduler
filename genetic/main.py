from __future__ import print_function
from scheduler import Scheduler

import unittest
import logging


def init_logging():
    logging.basicConfig(filename='genetic.log', level=logging.DEBUG)
    logging.debug("Logging is initialized")


def main():
    init_logging()
    s = Scheduler()


if __name__ == "__main__":
    main()
