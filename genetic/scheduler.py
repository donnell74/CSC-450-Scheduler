from __future__ import print_function
from copy import deepcopy
from copy import copy
from random import randint
from random import choice
from datetime import time, timedelta
from structures import *
from constraint import *
#import interface # uncomment to use export_schedule_xml 
import xml.etree.ElementTree as ET
import os.path


class SchedulerInitError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BreedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Scheduler:

    """Schedules all courses for a week"""

    def __init__(self, courses, rooms, time_slots_mwf, time_slots_tr, time_slot_divide, test = False):
        # eventually will include mwf and tr slots instead of general slots
        try:
            courses[0].code
        except:
            raise SchedulerInitError("Courses")

        try:
            assert type(rooms[0]) == str
        except:
            raise SchedulerInitError("Rooms")

        try:
            assert type(time_slots_mwf[0]) == str
        except:
            raise SchedulerInitError("Time Slots")

        try:
            assert type(time_slots_tr[0]) == str
        except:
            raise SchedulerInitError("Time Slots")

        self.time_slots_mwf = time_slots_mwf
        self.time_slots_tr = time_slots_tr
        self.time_slots = time_slots_mwf + time_slots_tr
        try:
            assert type(time_slot_divide) == int
            assert 0 < time_slot_divide and time_slot_divide <= min(len(self.time_slots_mwf), len(self.time_slots_tr))
        except:
            raise SchedulerInitError("Time Slot Divide")

        self.slot_divide = time_slot_divide
        self.courses = courses
        self.rooms = rooms
        self.weeks = [Week(rooms, self, test), Week(rooms, self, test),
                      Week(rooms, self, test), Week(rooms, self, test),
                      Week(rooms, self, test)]

        self.constraints = []
        self.max_fitness = 0

        # Number of courses
        self.num_courses = len(courses)
        # Courses grouped by credit hours
        self.separated = self.separate_by_credit(self.courses)

    def separate_by_credit(self, courses_list):
        """Groups the courses based on number of credit hours.
        IN: list of course objects
        OUT: dictionary with keys=credit hours and values=list of course objects"""
        courses_by_credits = {}
        for each_course in courses_list:
            # Case 1: New key-value pair (make new list)
            if each_course.credit not in courses_by_credits.keys():
                courses_by_credits[each_course.credit] = [each_course]
            # Case 2: Add to value's list for key
            else:
                courses_by_credits[each_course.credit].append(each_course)
        return courses_by_credits

    def add_constraint(self, name, weight, func, *args):
        """Adds an constraint to the schedule"""
        self.constraints.append(Constraint(name, weight, func, *args))
        self.max_fitness += weight

    def clear_constraints(self):
        """Removes all constraints from list"""
        self.constraints = []
        self.max_fitness = 0

    def calc_fitness(self, this_week):
        """Calculates the fitness score of a schedule"""
        total_fitness = 0
        for each_constraint in self.constraints:
            total_fitness += each_constraint.get_fitness(this_week)

        this_week.fitness = total_fitness

    def mutate(self, this_week):
        """Mutates a schedule by changing a course's time"""
        empty_slots = this_week.find_empty_time_slots()
        if len(empty_slots) == 0:
            # no mutation performed
            return this_week

        roll = randint(1, len(self.courses) - 1)
        random_course = self.courses[roll]
        old_slots = this_week.find_course(random_course)
        for each_old_slot in old_slots:
            # No longer assigned
            each_old_slot.remove_course()
        # Reassign
        self.randomly_fill_schedule(this_week, [random_course], empty_slots)

    def find_respective_time_slot(self, time_slot, week):
        """Finds the given time slot object in given week and returns it"""
        day = time_slot.info("Day")
        room = time_slot.info("Room")
        return week.find_time_slot(day, room, time_slot)

    def find_time_slots_from_cuts(self, this_week, slots_list):
        """For a given week, returns all time slots matching the slots list"""
        matching_slots = []

        # form times from slots_list
        times = []
        for each_slot in slots_list:
            # todo: Condense this
            start, end = each_slot.split('-')
            start = start.split(':')
            start = list(map(int, start))
            start = time(start[0], start[1])
            times.append(start)  # only care about start times right now

        full_list = this_week.list_time_slots()
        for each_slot in full_list:
            if each_slot.start_time in times:
                matching_slots.append(each_slot)

#        extras = "<slots_list>\n<item>%s</item></slots_list>\n<matching_slots>\n<item>%s</item></matching_slots>\n" %\
#                  ("</item>\n<item>".join(slots_list), \
#                   "</item>\n<item>".join([s.day + " - " + s.room.building + " - " + s.room.number + " - " \
#                       + str(s.start_time)[:-3] for s in matching_slots]))
#        interface.export_schedule_xml(this_week, extras, "find_time_slots_from_cuts_")

        return matching_slots

    def replace_time_slots(self, slotsA, slotsB):
        """Change all courses for matching time slots"""
        for i in slotsA:
            for j in slotsB:
                if i.start_time == j.start_time and i.room.number == j.room.number and \
                   i.room.day.day_code == j.room.day.day_code:
                    courseA = i.course
                    courseB = j.course
                    i.set_course(courseB)
                    j.set_course(courseA)
        return

    def assess_inconsistencies(self, this_week):
        """Returns a dictionary of surplus and lacking courses for a schedule/week
        IN: week object
        OUT: dictionary with keys surplus and lacking; former value is list of
             courses with surplus; latter is list of courses not
             scheduled for the week"""
        inconsistencies = {'surplus': [], 'lacking': []}
        full_list = this_week.list_time_slots()

        for course in self.courses:
            slots = this_week.find_course(course)
            num_slots = len(slots)
            if num_slots == 0:
                inconsistencies['lacking'].append(course)
            elif num_slots > course.credit:
                inconsistencies['surplus'].append(course)

        return inconsistencies

    def week_helper(self, time_slot, time_slot_list):
        """Gives the 5 timeslot objects and occupied status for each day in the same room,
        at the same time, with the same schedule/week as the given time slot object
        IN: list of time slot objects *for a schedule/week*, time slot object
        OUT: dictionary with occupied counter and unoccupied keys, with values being time slots
             for the week; also gives the objects in order by day and their occupation status
             in order by day"""
        helper = {'occupied': 0, 'unoccupied': [], 'in_order': [None, None, None, None, None],
                  'occupation': [0, 0, 0, 0, 0]}
        # Only need start time, not end time, because time slots on the same
        # day don't overlap
        marker = False  # marker for whether open or not for current
        this_time = time_slot.start_time
        this_room = time_slot.room.number
        for each_slot in time_slot_list:
            if each_slot.start_time == this_time and each_slot.room.number == this_room:
                # occupation status
                if each_slot.course is None:
                    marker = True
                    helper['unoccupied'].append(each_slot)
                else:
                    # occupied counter
                    helper['occupied'] += 1

                # day
                temp_day = each_slot.room.day.day_code
                if temp_day == 'm':
                    helper['in_order'][0] = each_slot
                    helper['occupation'][0] = 1 if marker else 0
                elif temp_day == 't':
                    helper['in_order'][1] = each_slot
                    helper['occupation'][1] = 1 if marker else 0
                elif temp_day == 'w':
                    helper['in_order'][2] = each_slot
                    helper['occupation'][2] = 1 if marker else 0
                elif temp_day == 'r':
                    helper['in_order'][3] = each_slot
                    helper['occupation'][3] = 1 if marker else 0
                else:
                    helper['in_order'][4] = each_slot
                    helper['occupation'][4] = 1 if marker else 0
                marker = False  # reset it
        # cleanup...take care of cases where time slot has been removed
        for entry in helper['in_order']:
            if entry is None:
                # occupied counter
                helper['occupied'] += 1
        return helper

    def resolve_inconsistencies(self, this_week, inconsistencies):
        """Removes excess courses and adds lacking courses to week.
        IN: (crossed) week object, inconsistencies dict with surplus and lacking
             both are list of courses
        OUT: (crossed) week object that represents all courses once"""
        full_list = this_week.list_time_slots()
        open_list = []

        for each_course in inconsistencies['surplus']:
            slots = this_week.find_course(each_course)
            for each_slot in slots:
                each_slot.remove_course()

        inconsistencies['lacking'].extend(inconsistencies['surplus'])

        # find all excess slots
        for i in full_list:
            if i.course is None:
                open_list.append(i)

        # fill in missing courses
        self.randomly_fill_schedule(
            this_week, inconsistencies['lacking'], open_list)

    def crossover(self, P1, P2):
        """Mixes weeks (schedules) P1 and P2 to create 2 children weeks, then corrects
        the children weeks as necessary
        IN: 2 parent schedules, P1 and P2
        OUT: 2 children schedules, C1 and C2, in a list"""
        output = []
        # the time slot(s) which will be moved between C1 and C2
        time_slots = self.time_slots[:self.slot_divide]

        C1 = P1.deep_copy()
        C2 = P2.deep_copy()
        # P1's slots to have its courses cloned on P2
        cutA = self.find_time_slots_from_cuts(C1, time_slots)
        # P2's slots to have its courses cloned on P1
        cutB = self.find_time_slots_from_cuts(C2, time_slots)
        # do the replacement
        self.replace_time_slots(cutA, cutB)

        for i in [C1, C2]:
            # figure out what have extra of/don't have
            inconsistencies = self.assess_inconsistencies(i)
            # clear the excess; try to schedule lacking
            self.resolve_inconsistencies(i, inconsistencies)
            inconsistencies = self.assess_inconsistencies(i)
            # THIS IS A BANDAID
            if len(inconsistencies["surplus"]) > 0:
                i.valid = False

            output.append(i)
        return output

    def breed(self):
        """Produces a set of schedules based of the current set of schedules"""
        try:
            assert len(self.weeks) > 1
            assert isinstance(self.weeks[0], Week)
        except:
            raise BreedError("Weeks")

        # combinations...(ex) 5 choose 2
        for each_week in range(0, len(self.weeks) - 1, 2):
            for each_other_week in range(each_week + 1, len(self.weeks), 2):
                children = self.crossover(
                    self.weeks[each_week], self.weeks[each_other_week])
                # Check for invalid children and delete them
                for each_child in children:
                    for each_course in self.courses:
                        # If scheduled for wrong number of slots
                        if (each_course.credit == 4) and (len(each_child.find_course(each_course)) != 4):
                            each_child.valid = False
                        elif (each_course.credit == 3):
                            for each_slot in each_child.find_course(each_course):
                                for each_other_slot in each_child.find_course(each_course):
                                    if each_slot.day in 'mwf' and (each_other_slot.day in 'tr' or
                                                                   len(each_child.find_course(each_course)) != 3) or \
                                        each_slot.day in 'tr' and (each_other_slot.day in 'mwf' or
                                                                   len(each_child.find_course(each_course)) != 2):
                                        each_child.valid = False
                    if not each_child.valid:
                        pass
                        #del children[children.index(each_child)]
                if len(children) > 0:
                    # Chance of mutation for each child
                    for each_child in children:
                        roll = randint(1, 3)
                        if roll == 2:
                            self.mutate(each_child)
                    # add to list of weeks
                    self.weeks.extend(children)
                else:
                    print("No valid children found!")
                    return
#                print(len(self.weeks))

    def evolution_loop(self):
        """Main loop of scheduler, run to evolve towards a high fitness score"""
        fitness_baseline = 10
        total_iterations = 0
        counter = 0
        MAX_TRIES = 10

        def week_slice_helper():
            valid_weeks = filter(lambda x: x.valid, self.weeks)
            valid_weeks.sort(key=lambda x: x.fitness, reverse=True)
            if len(valid_weeks) > 0:
                temp = filter(lambda x: not x.valid, self.weeks)[:5-len(valid_weeks)]
                temp.sort(key=lambda x: x.fitness, reverse=True)
                self.weeks = valid_weeks + temp

            self.weeks = self.weeks[:5]
            return valid_weeks

        while True:
            print('Generation counter:', counter + 1)
            for each_week in self.weeks:
                each_week.update_sections(self.courses)
                self.calc_fitness(each_week)
            #print([i.fitness for i in self.weeks])

            valid_weeks = week_slice_helper()
            week_slice_helper()
            if counter == MAX_TRIES - 1:
                print('Max tries reached; final output found')
                break

            print("Minimum fitness of the generation:",
                  min(i.fitness for i in self.weeks))
            print("Number of valid weeks for the generation:", str(len(valid_weeks)))

            #insufficient valid weeks
            if len(valid_weeks) == 0:
                print("Generating a new population")
                self.weeks = []
                self.generate_starting_population()
                total_iterations += 1
                counter += 1
                continue

            if min(i.fitness for i in self.weeks) == self.max_fitness and \
              len(self.weeks) >= 5 and len(valid_weeks) >= 5:
                break

            self.breed()
            total_iterations += 1
            counter += 1

        print("Final number of generations: ", total_iterations + 1)

    def time_slot_available(self, day, first_time_slot):
        for room in day.rooms:
            if room.number != first_time_slot.room.number:
                continue

            for t_slot in room:
                if t_slot == first_time_slot and t_slot.course == None:
                    return (t_slot, True)

        return (None, False)

    def randomly_fill_schedule(self, week_to_fill, courses_list, list_slots_to_fill):
        """Fills in random schedule for given week, courses, and time slots"""

        # helper function
        def find_index(time_slot, time_slot_list):
            """Finds index of time slot object in list of time slots for week"""
            counter = 0
            for each_slot in time_slot_list:
                if each_slot.room.number == time_slot.room.number and \
                   each_slot.start_time == time_slot.start_time and \
                   each_slot.room.day.day_code == time_slot.room.day.day_code:
                    return counter
                counter += 1
            print("Index not found")
            return

        def assign_and_remove(course, time_slot, slots_list, week):
            """Assigns course to time slot and removes time slot from list of time slots"""
            temp_room_index = time_slot.room_index
            temp_day_index = time_slot.day_index
            temp_slot_index = time_slot.slot_index

            i = find_index(time_slot, slots_list)
            week.days[temp_day_index].rooms[temp_room_index].schedule[
                temp_slot_index].set_course(course)
            del(slots_list[i])

        courses_by_credits = self.separate_by_credit(courses_list)
        # print(courses_by_credits)
        # main loop
        # todo...change var names to input rather than this
        each_week = week_to_fill
        # Make list of all time slots for week
        # todo...change var names to input ...
        list_of_time_slots = list_slots_to_fill
        # 5 hour case is easy because we handle it first...removes possibility of
        # selecting a week with courses
        try:
            for each_5 in courses_by_credits[5]:
                # Choose a random timeslot from the list of all time slots for
                # week
                random_slot = choice(list_of_time_slots)
                temp_pool = deepcopy(list_of_time_slots)
                done = False
                while len(temp_pool) > 0 and not done:
                    possibilities = self.week_helper(random_slot, temp_pool)
                    # each day open for that time and room
                    if len(possibilities['unoccupied']) == 5:
                        for each_assignee in possibilities['in_order']:
                            assign_and_remove(
                                each_5, each_assignee, list_of_time_slots, each_week)
                        done = True
                    # case that cannot schedule for this time and room
                    else:
                        # remove this timeslot and the other unoccupied in its
                        # week from temp pool
                        for to_remove in possibilities['unoccupied']:
                            i = find_index(to_remove, temp_pool)
                            del(temp_pool[i])
                        # get a new random time slot
                        random_slot = choice(temp_pool)
                # 2 ways out of while...test for which
                if len(temp_pool) == 0 and not done:
                    # impossible to schedule
                    week_to_fill.valid = False
        except KeyError:
            pass
        # other cases must consider how the week is taken up
        try:
            for each_4 in courses_by_credits[4]:
                # Choose a random timeslot from the list of all time slots for
                # week
                random_slot = choice(list_of_time_slots)
                temp_pool = deepcopy(list_of_time_slots)
                done = False
                while len(temp_pool) > 0 and not done:
                    # check rest of week's courses at same time and place
                    # (differ by day)
                    possibilities = self.week_helper(random_slot, temp_pool)
                    # case that whole week is open
                    if len(possibilities['unoccupied']) == 5:
                        for d in (0, 2, 4):
                            # MWF
                            assign_and_remove(
                                each_4, possibilities['in_order'][d], list_of_time_slots, each_week)
                        #T or R
                        j = randint(0, 1)
                        if j:
                            assign_and_remove(
                                each_4, possibilities['in_order'][1], list_of_time_slots, each_week)  # T
                        else:
                            assign_and_remove(
                                each_4, possibilities['in_order'][3], list_of_time_slots, each_week)  # R
                        done = True
                    # case that mwf and either t or r are open
                    elif possibilities['occupation'][0] and possibilities['occupation'][2] and \
                            possibilities['occupation'][4] and \
                            (possibilities['occupation'][1] or possibilities['occupation'][3]):
                        for d in (0, 2, 4):
                            # MWF
                            assign_and_remove(
                                each_4, possibilities['in_order'][d], list_of_time_slots, each_week)
                        if possibilities['occupation'][1]:
                            assign_and_remove(
                                each_4, possibilities['in_order'][1], list_of_time_slots, each_week)
                        else:
                            assign_and_remove(
                                each_4, possibilities['in_order'][3], list_of_time_slots, each_week)
                        done = True
                    # case that cannot schedule for this time and room
                    else:
                        # remove this timeslot and the other unoccupied in its
                        # week from temp pool
                        for to_remove in possibilities['unoccupied']:
                            i = find_index(to_remove, temp_pool)
                            del(temp_pool[i])
                        # get a new random time slot
                        random_slot = choice(temp_pool)
                # 2 ways out of while...test for which
                if len(temp_pool) == 0 and not done:
                    # impossible to schedule
                    week_to_fill.valid = False
        except KeyError:
            pass
        try:
            for each_3 in courses_by_credits[3]:
                # Choose a random timeslot from the list of all time slots for
                # week
                random_slot = choice(list_of_time_slots)
                temp_pool = deepcopy(list_of_time_slots)
                done = False
                while len(temp_pool) > 0 and not done:
                    # check rest of week's courses at same time and place
                    # (differ by day)
                    possibilities = self.week_helper(random_slot, temp_pool)
                    # case that whole week is open...MWF or TR
                    if len(possibilities['unoccupied']) == 5:
                        j = randint(0, 1)
                        # MWF
                        if j:
                            for d in (0, 2, 4):
                                assign_and_remove(
                                    each_3, possibilities['in_order'][d], list_of_time_slots, each_week)
                        # TR
                        else:
                            for d in (1, 3):
                                assign_and_remove(
                                    each_3, possibilities['in_order'][d], list_of_time_slots, each_week)
                        done = True
                    # case that mwf is open, but not tr
                    elif possibilities['occupation'][0] and possibilities['occupation'][2] and \
                            possibilities['occupation'][4]:
                        for d in (0, 2, 4):
                            assign_and_remove(
                                each_3, possibilities['in_order'][d], list_of_time_slots, each_week)
                        done = True
                    # case that tr is open, but not mwf
                    elif possibilities['occupation'][1] and possibilities['occupation'][3]:
                        for d in (1, 3):
                            assign_and_remove(
                                each_3, possibilities['in_order'][d], list_of_time_slots, each_week)
                        done = True
                    # case that cannot schedule for this time and room
                    else:
                        # remove this timeslot and the other unoccupied in its
                        # week from temp pool
                        for to_remove in possibilities['unoccupied']:
                            i = find_index(to_remove, temp_pool)
                            del(temp_pool[i])
                        # get a new random time slot
                        random_slot = choice(temp_pool)
                # 2 ways out of while...test for which
                if len(temp_pool) == 0 and not done:
                    # impossible to schedule
                    week_to_fill.valid = False
        except KeyError:
            pass
        # Case of 1 hour is very easy because we saved it for last--just take
        # whatever you find
        try:
            for each_1 in courses_by_credits[1]:
                assign_and_remove(
                    each_1, random_slot, list_of_time_slots, each_week)
        # case of no 1 hour courses
        except KeyError:
            pass

    def generate_starting_population(self):
        """Generates starting population"""
        for x in range(10):
            self.weeks.append(Week(self.rooms, self))

        for each_week in self.weeks:
            list_slots = each_week.list_time_slots()
            self.randomly_fill_schedule(each_week, self.courses, list_slots)
            # if impossible to generate (incomplete week)
            if not each_week.valid:
                del self.weeks[self.weeks.index(each_week)]
        if len(self.weeks) == 0:
            print("Could not schedule")
            return
        #for each_week in self.weeks:
            #self.calc_fitness(each_week)
            #each_week.print_concise()
