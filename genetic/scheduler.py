from __future__ import print_function
from random import randint
from structures import *
from datetime import time, timedelta

import logging


def morning_class(course, this_week):
    #Find course returns a list of time slots, but they should all be at the same time
    holds = this_week.find_course(course)[0].start_time < time(12, 0)
    return 1 if holds else 0


known_funcs = {"morning_class", morning_class}

class Constraint:
    def __init__(self, name, weight, func, course = None):
        if type(name) is not str:
            logging.error("Name is not a string")
            print("Name is not a string")
            return
        
        if type(weight) is not int:
            logging.error("Weight is not a string")
            print("Weight is not a string")
            return

        if not hasattr(func, '__call__'):
            if type(func) is str and not known_funcs.has_key(func):
                logging.error("Func string passed is not known")
                print("Func string passed is not known")
                return
            else:
                logging.error("Func passed is not a function")
                print("Func passed is not a function")
                return

        if not isinstance(course, Course):
            logging.error("Course is not of object type course")
            print("Course is not of object type course")
            return

        self.name = name
        self.weight = weight
        self.course = course
        if type(func) is str:
            self.func = func
        else:
            self.func = func

    def get_fitness(self, this_week):
        if self.course == None:
            return self.func(this_week) * self.weight
        else:
            return self.func(self.course, this_week) * self.weight


class Scheduler:
    """Schedules all courses for a week"""
    def __init__(self, courses, rooms):
        logging.debug("Scheduler init")
        if type(courses) is list:
            if not isinstance(courses[0], Course):
                logging.error("Courses is not a list of Course objects")
                print("Courses is not a list of Course objects")
                return
        else:
            logging.error("Courses is not a list")
            print("Courses is not a list")
            return

        if type(rooms) is not list:
            logging.error("Rooms is not a list")
            print("Rooms is not a list")
            return

        self.weeks = [Week(rooms), Week(rooms), Week(rooms), Week(rooms), Week(rooms)]
        self.constraints = []
        self.max_fitness = 0
        self.courses = courses
        self.rooms = rooms
        
        #Number of courses
        self.num_courses = len(courses)
        #Courses grouped by credit hours
        self.separate_by_credit(courses)
        #Number of groups of credits
        self.num_credits = len(self.courses_by_credits.keys())
        #print(self.weeks[0].find_time_slot('m', '11:00'))

    def separate_by_credit(self, courses):
        """Groups the courses based on number of credit hours.
        IN: list of course objects
        OUT: dictionary with keys=credit hours and values=list of course objects;
             dictionary with keys=credit hours and values=number of course objects"""
        courses_by_credits = {}
        num_courses_by_credits = {}
        for each_course in courses:
            #Case 1: New key-value pair (make new list)
            if each_course.credit not in courses_by_credits.keys():
                courses_by_credits[each_course.credit] = [each_course]
                num_courses_by_credits[each_course.credit] = 1
            #Case 2: Add to value's list for key
            else:
                courses_by_credits[each_course.credit].append(each_course)
                num_courses_by_credits[each_course.credit] += 1
        self.courses_by_credits = courses_by_credits
        self.num_courses_by_credits = num_courses_by_credits
        return


    def add_constraint(self, name, weight, func, course = None):
        self.constraints.append(Constraint(name, weight, func, course)) 
        self.max_fitness += weight
    

    def calc_fitness(self, this_week):
        """Calculates the fitness score of a schedule"""
        total_fitness = 0
        for each_constraint in self.constraints:
            total_fitness += each_constraint.get_fitness(this_week)

        this_week.fitness = total_fitness


    def mutate(self, func):
        """Mutates a schedule given an appropriate function"""
        if not hasattr(func, '__call__'):
            logging.error("Func passed is not a function")
            print("Func passed is not a function")
        

    def find_respective_time_slot(self, time_slot, week):
        """Finds the given time slot object in given week and returns it"""
        day = time_slot.info("Day")
        room = time_slot.info("Room")
        return week.find_time_slot(day, room, time_slot)


    def swap(self, course1, course2, schedule):
        """Performs swaps around 2 courses in a schedule
        IN: 2 Course objects, schedule object
        OUT: schedule object with swap performed"""
        #Time slot for course in P1
        time_slot_in_P1 = P1.find_course(course)
        #Corresponding time slot in P2:
        time_slot_respective_P2 = find_respective_time_slot(time_slot_in_P1, P2)
        #Time slot for course in P2
        time_slot_in_P2 = P2.find_course(course)
        #Corresponding time slot in P1:
        time_slot_respective_P1 = find_respective_time_slot(time_slot_in_P2, P1)
        #todo: check input types; log errors


    def crossover(self, P1, P2):
        """Performs a series of swaps on two schedules to produce children
        IN: 2 parent schedules, P1 and P2
        OUT: 2 children schedules, C1 and C2"""
        #Random number of swaps
        num_swaps = randint(1, self.num_courses)
        C1 = P1.deep_copy()
        C2 = P2.deep_copy()
        for swap in range(num_swaps):
            #Random credit hours selected
            credit = self.courses_by_credits[randint(1, self.num_credits)]
            #todo: perform the counts earlier
            course_a = self.courses_by_credits[credit][randint(1,
                self.num_courses_by_credits[credit])]
            course_b = self.courses_by_credits[credit][randint(1,
                self.num_courses_by_credits[credit])]
            swap(course_a, course_b, C1, C2)


    def breed(self):
        """Produces a set of schedules based of the current set of schedules"""
        for x in range(15):
            self.weeks.append(Week(self.rooms))

        self.randomly_fill_schedules()

    def evolution_loop(self):
        """Main loop of scheduler, run to evolve towards a high fitness score"""
        fitness_baseline = 30
        total_iterations = 0
        counter = 0
        MAX_TRIES = 50

        def week_slice_helper():
            self.weeks.sort(key=lambda x: x.fitness, reverse=True)
            self.weeks = self.weeks[:5]

        while True:
            for each_week in self.weeks:
                self.calc_fitness(each_week)

            week_slice_helper()
            if counter > MAX_TRIES:
                break

            if len(filter(lambda x: x.fitness <=fitness_baseline, self.weeks)) == 0:
                if fitness_baseline >= self.max_fitness:
                    break

                print(fitness_baseline, " : ", counter)
                fitness_baseline += 30
                counter = 0

            self.breed() #makes self.weeks a list of 20 new 
            total_iterations += 1 
            counter += 1

        print("Breeding iterations: ", total_iterations)


    def time_slot_available(self, day, first_time_slot):
        for room in day.rooms:
            if room.number != first_time_slot.room.number:
                continue

            for t_slot in room:
                if t_slot == first_time_slot and t_slot.course == None:
                    return (t_slot, True)
        
        return (None, False)


    def randomly_fill_schedules(self):
        #get all available time slots grouped by day
        for each_week in self.weeks:
            time_slots_by_day = dict([(day, list()) for day in "mtwrf"])
            for day in each_week.days:
                for room in day.rooms:
                    time_slots_by_day[day.day_code].extend([t for t in room])
            
            for courses_in_curr_credit in self.courses_by_credits.values()[::-1]:
                index = 0
                times_on_index = 0 
                while True:
                    if index == len(courses_in_curr_credit):
                        break

                    times_on_index += 1
                    each_course = courses_in_curr_credit[index]
                    day_schedule = ""
                    #if each_course.credit == 3
                    day_schedule = "tr" if random.randint(0,1) else "mwf"
                    if each_course.credit == 4:
                        day_schedule = "mtwf" if random.randint(0,1) else "mwrf"
                    elif each_course.credit == 5:
                        day_schedule = "mtwrf"

                    should_index = True
                    rand_time_slot = time_slots_by_day[day_schedule[0]][random.randint(0, len(time_slots_by_day[day_schedule[0]])-1)]
                    to_schedule_lyst = [rand_time_slot]
                    for day_code in day_schedule[1:]:
                        time_slot_to_schedule, time_found = self.time_slot_available(each_week[day_code], rand_time_slot)
                        to_schedule_lyst.append(time_slot_to_schedule) 
                        should_index = should_index and time_found 

                    if should_index or times_on_index > 10:
                        if times_on_index > 10:
                            #uncomment for output of bad courses
                            #print("Unable to schedule ", str(each_course))
                            pass
                        else:
                            for t_slot in to_schedule_lyst:
                                t_slot.course = each_course
                        index += 1
                        times_on_index = 1

                    

