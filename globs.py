from genetic import interface, scheduler, constraint

def init(): # call globals.init() from main
    global courses, course_titles, rooms, time_slots, instructors, mainScheduler, start_times, end_times

    # Get all courses and instructors from file
    input_path = "genetic/seeds/Input.xml"
    instructors = interface.create_instructors_from_courses(input_path)
    instructors_dict = dict(zip([inst.name for inst in instructors], [inst for inst in instructors]))
    courses = interface.create_course_list_from_file(input_path, instructors_dict)
    rooms = interface.create_room_list_from_file(input_path)
    time_slots_mwf, time_slots_tr = interface.create_time_slot_list_from_file(input_path)
    course_titles = [course.code for course in courses]

    # stuff that should be moved to a file
    time_slot_divide = 2 #todo: remove this from xml
    #DO NOT DO THIS AGAIN
    #GREG IS SORRY
    try:
        mainScheduler
    except:
        mainScheduler = scheduler.Scheduler(courses, rooms, time_slots_mwf, time_slots_tr, time_slot_divide)
        print "Slot divide is", mainScheduler.slot_divide
        mainScheduler.generate_starting_population(just_one = True)

        #prereqs computation and display
        prereqs = interface.get_prereqs(input_path, courses)
        prereqs = interface.get_extended_prereqs(prereqs, courses)
        '''for prereq in prereqs:
            print " ".join([c.absolute_course for c in prereq.courses]) + ":" + \
                  " ".join([c.absolute_course for c in prereq.prereqs])'''

        # Add all mandatory constraints here
        mainScheduler.add_constraint("instructor conflict", 0,
                                    constraint.instructor_conflict,
                                    [instructors])
        mainScheduler.add_constraint("sequential_time_different_building_conflict", 0,
                                    constraint.sequential_time_different_building_conflict,
                                    [instructors])
        mainScheduler.add_constraint("subsequent courses", 0,
                                    constraint.num_subsequent_courses,
                                    [instructors])
        mainScheduler.add_constraint("capacity checking", 0,
                                    constraint.ensure_course_room_capacity,
                                    [])
        mainScheduler.add_constraint("no overlapping courses", 0,
                                    constraint.no_overlapping_courses,
                                    [])
        mainScheduler.add_constraint("computer requirement", 0,
                                    constraint.ensure_computer_requirement,
                                    [])
        mainScheduler.add_constraint("course sections at different times", 0,
                                    constraint.course_sections_at_different_times,
                                    [courses[:-1]])  # the last item is "All", ignore it

    # used for gui strings
    # must be in military time
    # todo: make function to do the below
    start_times = sorted(list(set([':'.join(str(slot.start_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
    end_times = sorted(list(set([':'.join(str(slot.end_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
