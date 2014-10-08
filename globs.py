from genetic import interface, scheduler

def init(): # call globals.init() from main
    global courses, course_titles, rooms, time_slots, instructors, mainScheduler, start_times, end_times

    # Get all courses and instructors from file
    inp = open("genetic/seeds/Scheduler.csv")
    courses_and_details = interface.csv_dict_reader(inp)
    instructors = interface.get_instructors(courses_and_details)
    courses_credits_and_instructors = \
        interface.include_instructors_in_dict(courses_and_details, instructors)
    courses = interface.get_courses(courses_credits_and_instructors)
    course_titles = [course.code for course in courses]

    # stuff that should be moved to a file
    rooms = ["CHEK212", "CHEK105", "CHEK213"]
    time_slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    time_slot_divide = 2
    #DO NOT DO THIS AGAIN
    #GREG IS SORRY
    try:
        mainScheduler
    except:
        mainScheduler = scheduler.Scheduler(courses, rooms, time_slots, time_slot_divide)
        mainScheduler.generate_starting_population()

        # used for gui strings
        start_times = [':'.join(str(slot.start_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()]
        end_times = [':'.join(str(slot.end_time).split(":")[0:-1]) for slot in mainScheduler.weeks[0].list_time_slots()]
 
