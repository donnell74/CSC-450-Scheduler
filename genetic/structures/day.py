from __future__ import print_function
from copy import copy
import structures
from weakref import ref

class Day:
    """ Represents a single day, consisting of a list of room objects """

    def __init__(self, rooms, day_code, this_week, test = False):
        if test:
            self.week = this_week
        else:
            self.week = ref(this_week)
        if day_code.lower() in 'mtwrf':
            self.day_code = day_code
        else:
            print("Day code was not recognized")
            return

        room_object_list = []
        """
        'rooms' is a list of tuples in the form:
            (building, number, capacity, has_computers)
        """
        for room in rooms:
            room_object = structures.Room(building = room[0],
                                          number = room[1],
                                          capacity = room[2],
                                          has_computers = room[3],
                                          this_day = self,
                                          test = test)
            room_object_list.append(room_object)

        self.rooms = room_object_list

    def info(self, query):
        """
        Goes up the object hierarchy to find object for given day
        Possible queries: week, schedule
        IN: query string
        OUT: object of query's type for given day
        """
        if query not in ["Week", "Schedule"]:
            print("Invalid query for Day")
            return
        elif query == "Week":
            return self.week()
        elif query == "Schedule":
            return self.week().schedule()

    def get_room(self, query_number):
        for each_room in self.rooms:
            if each_room.number == query_number:
                return each_room
        return None

    def __str__(self):
        return "-----------------------\n" + \
            "Day: " + self.day_code + '\n' + "Rooms:\n" + \
            "\n".join([str(r) for r in self.rooms])
