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


class FilterError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MalformedTimeslotError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



class Scheduler:

    """Schedules all courses for a week"""

    def __init__(self, courses, rooms, time_slots_mwf, time_slots_tr, time_slot_divide, test = False):
        if type(courses) == list:
            if len(courses) != 0:
                if not all(isinstance(each_course, Course) for \
                        each_course in courses):
                   raise SchedulerInitError("Courses - Not all of type Course") 
            else:
                raise SchedulerInitError("Courses - List has no elements")
        else:
            raise SchedulerInitError("Courses - Not a list")

        if type(rooms) == list:
            if len(rooms) != 0:
                if not all(isinstance(each_room, tuple) for each_room in rooms):
                    raise SchedulerInitError("Rooms - Not all tuple type")
                else:
                    for each_room in rooms:
                        if not all(isinstance(part, str) for part in each_room):
                            raise SchedulerInitError("Rooms - Not all parts are str type")
            else:
                 raise SchedulerInitError("Rooms - List has no elements")
        else:
            raise SchedulerInitError("Rooms - Not a list")

        if type(time_slots_mwf) == list:
            if len(time_slots_mwf) != 0:
                if not all(isinstance(each_slot, str) for \
                        each_slot in time_slots_mwf):
                    raise SchedulerInitError("Time Slot MWF - \
                            Not all string type")
            else:
                 raise SchedulerInitError("Time Slot MWF -\
                         List has no elements")
        else:
            raise SchedulerInitError("Time Slot MWF - Not a list")

        if type(time_slots_tr) == list:
            if len(time_slots_tr) != 0:
                if not all(isinstance(each_slot, str) for \
                        each_slot in time_slots_tr):
                    raise SchedulerInitError("Time Slot TR - \
                            Not all string type")
            else:
                 raise SchedulerInitError("Time Slot TR -\
                         List has no elements")
        else:
            raise SchedulerInitError("Time Slot TR - Not a list")

        self.time_slots_mwf = time_slots_mwf
        self.time_slots_tr = time_slots_tr
        self.time_slots = time_slots_mwf + time_slots_tr
        if type(time_slot_divide) == int:
            if time_slot_divide < 0 and \
                time_slot_divide >= min(len(self.time_slots_mwf), 
                                        len(self.time_slots_tr)):
                raise SchedulerInitError("Time Slot Divide - Not valid number")
        else:
            raise SchedulerInitError("Time Slot Divide - Not valid number")

        self.slot_divide = time_slot_divide
        self.courses = courses
        self.rooms = rooms
        self.weeks = []

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
        
    def delete_list_constraints(self, items):
        """Removes some constraints from list"""
        for i in sorted(items, reverse=True):
            self.max_fitness -= self.constraints[i].weight
            del self.constraints[i]

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


    def find_time_slots_from_cuts(self, this_week, slots_list):
        """For a given week, returns all time slots matching the slots list"""
        matching_slots = []

        # form times from slots_list
        start_times = []
        end_times = []
        for each_slot in slots_list:
            start, end = each_slot.split('-')
            start = start.split(':')
            start = list(map(int, start))
            start = time(start[0], start[1])
            start_times.append(start)  

            end = end.split(':')
            end = list(map(int, end))
            end = time(end[0], end[1])
            end_times.append(end) 

        full_list = this_week.list_time_slots()
        for each_slot in full_list:
            if each_slot.start_time in start_times and\
               each_slot.end_time in end_times:
                matching_slots.append(each_slot)

        return matching_slots

    def replace_time_slots(self, slotsA, slotsB):
        """Change all courses for matching time slots ("swaps")
        IN: two lists of time slots (cuts) for 2 weeks
        OUT: two lists have been 'swapped'"""
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
        if len(self.weeks) < 2:
            raise BreedError("Weeks is not the correct length")

        if not all(isinstance(each_week, Week) for \
                each_week in self.weeks):
            raise BreedError("An element in weeks is not a Week object")


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
        MAX_TRIES = 20

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
            if counter == MAX_TRIES - 1:
                print('Max tries reached; final output found')
                break

            print("Minimum fitness of the generation:",
                  min(i.fitness for i in self.weeks))
            print("Number of valid weeks for the generation:", str(len(valid_weeks)))

            #insufficient valid weeks
            """
            if len(valid_weeks) == 0:
                print("Generating a new population")
                self.weeks = []
                self.generate_starting_population()
                total_iterations += 1
                counter += 1
                continue
                """

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


    def find_index(self, time_slot, time_slot_list):
        """Finds index of time slot object in list of time slots for week"""
        counter = 0
        for each_slot in time_slot_list:
            if each_slot.room.number == time_slot.room.number and \
               each_slot.start_time == time_slot.start_time and \
               each_slot.end_time == each_slot.end_time and \
               each_slot.room.day.day_code == time_slot.room.day.day_code:
                return counter
            counter += 1
        print("Index not found")
        return


    def assess_time_slot_row_for_open_slots(self, time_slots):
        """Generates a dictionary describing the trends of the list of time slots
        IN: list of time slot objects
        OUT: dictionary describing type of time slots, list of time slot objects,
             and open days
        Type: 0 for undefined, 1 for mwf, 2 for tr, 3 for both"""
        row_dict = {'days': '', 'time_slots': [], 'type': 0}
        for each_time_slot in time_slots:
            if each_time_slot.course is None:
                row_dict['time_slots'].append(each_time_slot)
                row_dict['days'] += each_time_slot.day

                if each_time_slot.isTR and row_dict['type'] == 0:
                    row_dict['type'] = 2
                elif not each_time_slot.isTR and row_dict['type'] == 0:
                    row_dict['type'] = 1
                elif (each_time_slot.isTR and row_dict['type'] == 1) or \
                     (not each_time_slot.isTR and row_dict['type'] == 2):
                    row_dict['type'] = 3
                elif (not each_time_slot.isTR and row_dict['type'] == 1) or \
                     (each_time_slot.isTR and row_dict['type'] == 2):
                    pass
                else:
                    print(each_time_slot.isTR)
                    print(row_dict['type'])
                    raise MalformedTimeslotError("Timeslot does not have a isTR attribute")

        return row_dict


    def assign_and_remove(self, course, time_slot, tr_slots, mwf_slots, slots_list, week):
        """Assigns course to time slot and removes time slot from list of time slots"""
        #i = self.find_index(time_slot, slots_list)
        schedule_slot = week.find_matching_time_slot(time_slot)
        i = self.find_index(schedule_slot, slots_list)
        schedule_slot.set_course(course)
        del(slots_list[i])


    def filter_for_generator(self, courses_list, list_of_slots_to_fill):
        """Filters tr slots, mwf slots, prescheduled courses, and regular courses"""
        filtered_input = {}
        tr_slots = filter(lambda x: x.isTR, list_of_slots_to_fill)
        mwf_slots = filter(lambda x: not x.isTR, list_of_slots_to_fill)
        prescheduled = filter(lambda x: x.is_prescheduled, courses_list)
        regular = filter(lambda x: not x.is_prescheduled, courses_list)
        filtered_input['tr'] = tr_slots
        filtered_input['mwf'] = mwf_slots
        filtered_input['prescheduled'] = prescheduled
        filtered_input['regular'] = regular
        return filtered_input


    def preschedule(self, week_to_fill, course):
        """Manually schedules a course at its designated time"""
        if not course.is_prescheduled:
            #log error
            return
        else:
            time_slots = week_to_fill.find_prescheduled_times(course)
            for each_time_slot in time_slots:
                if each_time_slot.course is not None:
                    #log error
                    pass
                each_time_slot.set_course(course)


    def schedule_5_hour_course(self, course, tr_slots, mwf_slots, list_of_slots, this_week):
        """Randomly schedule a 5 hour course"""
        if course.credit != 5:
            raise FilterError("Schedule 5 hour course")

        random_slot = choice(mwf_slots)
        current_pool = deepcopy(mwf_slots)
        done = False
        while len(current_pool) > 0 and not done:
            possibilities = this_week.find_matching_time_slot_row(random_slot)
            possibilities = self.assess_time_slot_row_for_open_slots(possibilities)
            # each day open for that time and room
            if len(possibilities['time_slots']) == 5:
                for each_assignee in possibilities['time_slots']:
                    self.assign_and_remove(
                        course, each_assignee, tr_slots, mwf_slots, list_of_time_slots, this_week)
                done = True
            # case that cannot schedule for this time and room
            else:
                # remove this timeslot and the other unoccupied in its
                # week from temp pool
                for to_remove in possibilities['time_slots']:
                    i = self.find_index(to_remove, current_pool)
                    del(current_pool[i])
                # get a new random time slot
                random_slot = choice(current_pool)
        #status
        return len(current_pool) == 0 and not done


    def schedule_4_hour_course(self, course, tr_slots, mwf_slots, list_of_time_slots, this_week):
        """Randomly schedule a 4 hour course"""
        if course.credit != 4:
            raise FilterError("Schedule 4 hour course")

        random_slot = choice(list_of_time_slots)
        current_pool = deepcopy(list_of_time_slots)
        done = False
        while len(current_pool) > 0 and not done:
            possibilities = this_week.find_matching_time_slot_row(random_slot)
            possibilities = self.assess_time_slot_row_for_open_slots(possibilities)
            # each day open for that time and room
            if len(possibilities['time_slots']) == 5:
                #MWF
                for each_slot in possibilities['time_slots']:
                    if each_slot.day in 'mwf':
                        self.assign_and_remove(
                            course, each_slot, tr_slots, mwf_slots,
                            list_of_time_slots, this_week)
                #T or R
                j = randint(0, 1)
                if j:
                    for each_slot in possibilities['time_slots']:
                        if each_slot.day == 't':
                            self.assign_and_remove(
                                course, each_slot, tr_slots, mwf_slots,
                                list_of_time_slots, this_week)  # T
                else:
                    for each_slot in possibilities['time_slots']:
                        if each_slot.day == 'r':
                            self.assign_and_remove(
                                course, each_slot, tr_slots, mwf_slots,
                                list_of_time_slots, this_week)  # R
                done = True
            # case that mwf and either t or r are open
            elif all([x in possibilities['days'] for x in 'mwf']) and \
                    (all([x in possibilities['days'] for x in 't']) or \
                     all([x in possibilities['days'] for x in 'r'])):
                for each_slot in possibilities['time_slots']:
                    if each_slot.day in 'mwf':
                        self.assign_and_remove(
                            course, each_slot, tr_slots, mwf_slots,
                            list_of_time_slots, this_week)
                if all([x in possibilities['days'] for x in 't']):
                    for each_slot in possibilities['time_slots']:
                        if each_slot.day in 't':
                            self.assign_and_remove(
                                course, each_slot, tr_slots, mwf_slots,
                                list_of_time_slots, this_week)
                else:
                    for each_slot in possibilities['time_slots']:
                        if each_slot.day in 'r':
                            self.assign_and_remove(
                                course, each_slot, tr_slots, mwf_slots,
                                list_of_time_slots, this_week)
                done = True
            # case that cannot schedule for this time and room
            else:
                # remove this timeslot and the other unoccupied in its
                # week from temp pool
                for to_remove in possibilities['time_slots']:
                    i = self.find_index(to_remove, current_pool)
                    del(current_pool[i])
                # get a new random time slot
                random_slot = choice(current_pool)
        #status
        return len(current_pool) == 0 and not done


    def schedule_3_hour_course(self, course, tr_slots, mwf_slots, list_of_time_slots, this_week):
        """Randomly schedule a 3 hour course"""
        if course.credit != 3:
            raise FilterError("Schedule 3 hour course")

        random_slot = choice(list_of_time_slots)
        current_pool = deepcopy(list_of_time_slots)
        done = False
        while len(current_pool) > 0 and not done:
            possibilities = this_week.find_matching_time_slot_row(random_slot)
            possibilities = self.assess_time_slot_row_for_open_slots(possibilities)
            # each day open for that time and room
            if len(possibilities['time_slots']) == 5:
                # MWF
                if not random_slot.isTR:
                    for each_slot in possibilities['time_slots']:
                        if each_slot.day in 'mwf':
                            self.assign_and_remove(
                                course, each_slot, tr_slots, mwf_slots,
                                list_of_time_slots, this_week)
                            #print(possibilities['in_order'][d])
                # TR
                else:
                    for each_slot in possibilities['time_slots']:
                        if each_slot.day in 'tr':
                            self.assign_and_remove(
                                course, each_slot, tr_slots, mwf_slots,
                                list_of_time_slots, this_week)
                done = True
            # case that mwf is open, but not tr
            elif all([x in possibilities['days'] for x in 'mwf']):
                for each_slot in possibilities['time_slots']:
                    if each_slot.day in 'mwf':
                        self.assign_and_remove(
                            course, each_slot,
                            tr_slots, mwf_slots, list_of_time_slots, this_week)
                done = True
            # case that tr is open, but not mwf
            elif all([x in possibilities['days'] for x in 'tr']) and possibilities['type'] == 2:
                for each_slot in possibilities['time_slots']:
                    if each_slot.day in 'tr':
                        self.assign_and_remove(
                            course, each_slot,
                            tr_slots, mwf_slots, list_of_time_slots, this_week)
                done = True
            # case that cannot schedule for this time and room
            else:
                # remove this timeslot and the other unoccupied in its
                # week from temp pool
                for to_remove in possibilities['time_slots']:
                    i = self.find_index(to_remove, current_pool)
                    del(current_pool[i])
                # get a new random time slot
                random_slot = choice(current_pool)
        #status
        return not done


    def schedule_1_hour_course(self, course, tr_slots, mwf_slots, list_of_slots, this_week):
        """Randomly schedule a 1 hour course"""
        #COME BACK TO
        if course.credit != 1:
            raise FilterError("Schedule 1 hour course")

        random_slot = choice(list_of_time_slots)
        current_pool = deepcopy(list_of_time_slots)
        done = False
        while len(temp_pool) > 0 and not done:
            possibilities = self.week_helper(random_slot, temp_pool)
            # each day open for that time and room
            if len(possibilities['unoccupied']) > 0:
                for each_assignee in possibilities['in_order']:
                    assign_and_remove(
                        course, each_assignee, tr_slots, mwf_slots, list_of_time_slots, this_week)
                done = True
            # case that cannot schedule for this time and room
            else:
                # remove this timeslot and the other unoccupied in its
                # week from temp pool
                for to_remove in possibilities['unoccupied']:
                    i = self.find_index(to_remove, current_pool)
                    del(temp_pool[i])
                # get a new random time slot
                random_slot = choice(current_pool)
        #status
        return len(current_pool) == 0 and not done


    def randomly_fill_schedule(self, week_to_fill, courses_list, list_of_slots_to_fill):
        """Fills in random schedule for given week, courses, and time slots"""
        filtered = self.filter_for_generator(courses_list, list_of_slots_to_fill)
        tr_slots = filtered['tr']
        mwf_slots = filtered['mwf']
        prescheduled = filtered['prescheduled']
        regular = filtered['regular'] #regular courses...not prescheduled

        for each_course in prescheduled:
            try:
                self.manually_fill_schedule(week_to_fill, each_course)
            except: #specifically for error from above
                week_to_fill.valid = False
        for each_course in regular:
            if each_course.capacity > 70:
                list_of_slots_to_fill = filter(lambda x: x.room.capacity > 70, list_of_slots_to_fill)

            if each_course.credit == 5:
                failure = self.schedule_5_hour_course(each_course, tr_slots, mwf_slots,
                                                      list_of_slots_to_fill, week_to_fill)
            elif each_course.credit == 4:
                failure = self.schedule_4_hour_course(each_course, tr_slots, mwf_slots,
                                                      list_of_slots_to_fill, week_to_fill)
            elif each_course.credit == 3:
                failure = self.schedule_3_hour_course(each_course, tr_slots, mwf_slots,
                                                      list_of_slots_to_fill, week_to_fill)
            elif each_course.credit == 1:
                failure = self.schedule_1_hour_course(each_course, tr_slots, mwf_slots,
                                                      list_of_slots_to_fill, week_to_fill)
            else:
                #error
                return
            if failure:
                #cannot schedule in present situation
                print("failure")
                week_to_fill.valid = False
        '''printed = False
        print("Final schedule:")
        for time_slot in week_to_fill.list_time_slots():
                if time_slot.course is not None:
                    print(time_slot)
                    printed = True
        if not printed:
            print("***Final schedule is empty!***")'''


    def generate_starting_population(self):
        """Generates starting population"""
        for x in range(15):
            self.weeks.append(Week(self.rooms, self))

        for each_week in self.weeks:
            list_slots = each_week.list_time_slots()
            self.randomly_fill_schedule(each_week, self.courses, list_slots)
            # if impossible to generate (incomplete week)
            #if not each_week.valid:
            #    del self.weeks[self.weeks.index(each_week)]
        if len(self.weeks) == 0:
            print("Could not schedule")
            return
        #for each_week in self.weeks:
            #self.calc_fitness(each_week)
            #each_week.print_concise()
