from genetic import interface, scheduler, constraint
import os

def init(): # call globals.init() from main
    global courses, course_titles, rooms, time_slots, instructors, mainScheduler, start_times, end_times

    xml_input_path = "genetic/seeds/Input.xml"
    yaml_input_path = "genetic/seeds/Input.yaml"

    # Find input seed from file
    """
    XML is preferred, but if Input.xml is not found, an attempt to find Input.yaml will be made
    and if file is present, it will be converted to XML before proceding
    """
    if os.path.isfile(xml_input_path) == False: #if there is no xml input, check for yaml
        if os.path.isfile(yaml_input_path) == False: #if neither xml nor yaml, return
            print("No valid input found. Please put put an input seed named 'Input.yaml' or " +
                  "'Input.xml' in ./genetic/seeds/ and try again")
            return
        else:
            interface.create_xml_from_yaml(yaml_input_path) #create xml from yaml

    # Now that we have valid XML input, create requisite objects from file
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
