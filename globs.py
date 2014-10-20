from genetic import interface, scheduler

def init(): # call globals.init() from main
    global courses, course_titles, rooms, time_slots, instructors, mainScheduler, start_times, end_times

    # Get all courses and instructors from file
    input_path = "genetic/seeds/Input.xml"
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
    print rooms

    # stuff that should be moved to a file
    time_slot_divide = 2 #todo: remove this from xml
    #DO NOT DO THIS AGAIN
    #GREG IS SORRY
    try:
        mainScheduler
    except:
        mainScheduler = scheduler.Scheduler(courses, rooms, time_slots, time_slot_divide)
        mainScheduler.generate_starting_population()
        print(str(len(mainScheduler.weeks)))
        for week in mainScheduler.weeks:
            next = raw_input("press enter")
            print week
    
    # used for gui strings
    # must be in military time
    # todo: make function to do the below
    start_times = sorted(list(set([':'.join(str(slot.start_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
    end_times = sorted(list(set([':'.join(str(slot.end_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()])))
