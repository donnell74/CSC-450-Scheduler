from genetic import interface, scheduler

def init(): # call globals.init() from main
    global courses, course_titles, rooms, time_slots, instructors, mainScheduler, start_times, end_times

    # Get all courses and instructors from file
    '''input_path = "genetic/seeds/Input.xml"
    instructors = interface.create_instructors_from_courses(input_path)
    instructors_dict = dict(zip([inst.name for inst in instructors], [inst for inst in instructors]))
    courses = interface.create_course_list_from_file(input_path, instructors_dict)
    rooms = interface.create_room_list_from_file(input_path)
    time_slots = interface.create_time_slot_list_from_file(input_path)
    course_titles = [course.code for course in courses]
    
    for course in courses:
        print course.code, course.credit, course.instructor
    
    print
    for instructor in instructors:
        print instructor.name
        for course in instructor.courses:
            print course.code
        print
    
    print time_slots
    print course_titles
    print rooms'''

     # Get all courses and instructors from file
    inp = open("genetic/seeds/Scheduler.csv")
    courses_and_details = interface.csv_dict_reader(inp)
    instructors = interface.get_instructors(courses_and_details)
    courses_credits_and_instructors = \
    interface.include_instructors_in_dict(courses_and_details, instructors)
    courses = interface.get_courses(courses_credits_and_instructors)
    course_titles = [course.code for course in courses]
    prereqs = interface.get_prereqs(courses_credits_and_instructors, courses)
    prereqs = interface.get_extended_prereqs(prereqs, courses)
    rooms = ["CHEK 105", "CHEK 212", "CHEK 213", "GLAS 001", "TEMP 001"]
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    '''for prereq in prereqs:
        print "absolute course:", prereq.absolute_course
        for course in prereq.courses:
            print course
        print'''

    # stuff that should be moved to a file
    time_slot_divide = 2 #todo: remove this from xml
    #DO NOT DO THIS AGAIN
    #GREG IS SORRY
    try:
        mainScheduler
    except:
        mainScheduler = scheduler.Scheduler(courses, rooms, time_slots, time_slot_divide)
        mainScheduler.generate_starting_population()
    
    # used for gui strings
    # must be in military time
    # todo: make function to do the below
    start_times = sorted(list(set([':'.join(str(slot.start_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
    end_times = sorted(list(set([':'.join(str(slot.end_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
