from genetic import interface, scheduler, constraint
import os

def init(): # call globals.init() from main
    global courses, course_titles, rooms, time_slots, instructors, mainScheduler, start_times, end_times

    yaml_input_path = "genetic/seeds/Input.yaml"
    yaml_constraint_path = "genetic/seeds/default_constraints.yaml"

    # Create XML input from YAMl (Input.yaml)
    if os.path.isfile(yaml_input_path) == False:
        print("No valid input found. Please put put an input seed named 'Input.yaml' or " +
                  "'Input.xml' in ./genetic/seeds/ and try again")
        return
    else:
        interface.create_xml_input_from_yaml(yaml_input_path) #create xml from yaml

    # Now that we have valid XML input, create requisite objects from file
    xml_input_path = "genetic/seeds/Input.xml"
    instructors = interface.create_instructors_from_courses(xml_input_path)
    instructors_dict = dict(zip([inst.name for inst in instructors], [inst for inst in instructors]))
    courses = interface.create_course_list_from_file(xml_input_path, instructors_dict)
    rooms = interface.create_room_list_from_file(xml_input_path)
    time_slots_mwf, time_slots_tr = interface.create_time_slot_list_from_file(xml_input_path)
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
        prereqs = interface.get_prereqs(xml_input_path, courses)
        prereqs = interface.get_extended_prereqs(prereqs, courses)
        '''for prereq in prereqs:
            print " ".join([c.absolute_course for c in prereq.courses]) + ":" + \
                  " ".join([c.absolute_course for c in prereq.prereqs])'''

        # Add all mandatory/hard constraints here
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
                                    [courses])

        labs = []
        for each_course in mainScheduler.courses:
            if each_course.is_lab:
                labs.append(each_course)

        mainScheduler.add_constraint("labs on tr", 0,
                                     constraint.lab_on_tr,
                                     [labs])

        mainScheduler.num_hard_constraints = len(mainScheduler.constraints)

        # Create list of default constraints from YAML (default_constraints.yaml)
        if os.path.isfile(yaml_constraint_path):
            # found default constraint file
            interface.create_constraints_from_yaml(yaml_constraint_path, mainScheduler, instructors)

    # used for gui strings
    # must be in military time
    # todo: make function to do the below
    start_times = sorted(list(set([':'.join(str(slot.start_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
    end_times = sorted(list(set([':'.join(str(slot.end_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
