from __future__ import print_function
from datetime import time, timedelta
import logging

class Day:
    def __init__(self, rooms, day_code):
        self.rooms = [Room(number) for number in rooms]
        if day_code.lower() in 'mtwrf':
            self.day_code = day_code
        else:
            logging.error("Day code was not recongized")
            print("Day code was not recongized")
            return

    def __str__(self):
        return "Day: " + self.day_code + '\n' + "Rooms:\n" + \
               "".join([str(r) + '\n' for r in self.rooms])

class Room:
    def __init__(self, number, time_slots = ['00:00-10:00', '11:00-15:00']):
        self.number = number
        self.schedule = self.generate_time_slots(time_slots)

    def generate_time_slots(self, time_slots):
        this_schedule = []
        for each_slot in time_slots:
            start, end = each_slot.split('-')
            this_schedule.append(TimeSlot(start.split(':'), end.split(':')))

        return this_schedule

    def __str__(self):
        return self.number + "\n" + "\n".join([str(t) for t in self.schedule])


class TimeSlot:
    def __init__(self, start_time, end_time, course = None):
        try:
            #make sure we are given 4 integers for times
            start_time = list(map(int, start_time))
            end_time = list(map(int, end_time))
        except ValueError:
            logging.error("Time slot unavailable with times given")
            print("Time slot unavailable with times given")
            return

        self.start_time = time(start_time[0], start_time[1])
        self.end_time = time(end_time[0], end_time[1])
        self.course = course
        self.duration = self.find_duration(start_time, end_time)

    def find_duration(self, start_time, end_time):
        duration_hours = (end_time[0] - start_time[0]) * 60
        duration_min = end_time[1] - start_time[1]
        return duration_hours + duration_min

    def __str__(self):
        return "Course:%s\nStart time:%s\nEnd time:%s\nDuration:%s" % \
               (self.course, str(self.start_time), str(self.end_time),
                self.duration)


class Week:
    def __init__(self, rooms):
        self.days = [Day(rooms, day_code) for day_code in 'mtwrf']

    def __str__(self):
        return "".join([str(d) for d in self.days])

class Course:
    def __init__(self, code, credit):
        self.code = code
        self.credit = credit

#Todo: decide on week/schedule
class Schedule:
    def __init__(self):
        pass
