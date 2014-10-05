    ##################################################################
    # something about the loops in the "all courses" funtions        #
    # causes weird results in the CSVs, for example:                 #
    # CSC333 mmwwrrf CHEK212 09:00:00-10:00:00                       #
    # CSC325 mwf CHEK105 09:00:00-10:00:00                           #
    # CSC450 ttr CHEK212 10:00:00-11:00:00                           #
    # CSC232 tr CHEK105 10:00:00-11:00:00                            #
    #                                                                #
    # The days are strange, but the times are correctly constrained. #
    ##################################################################


def all_before_time(this_week, args):
    """ iterates through courses in the schedule to make sure
     none are before a specific time
     Timeslot should be a time object:  time(12, 0) """
    args = args[0]  # args is read in as a tuple like: ([args],)
    hold = False
    for c in this_week.schedule.courses: # access list of courses
        hold = this_week.find_course(c)[0].start_time < args[1]
        if hold == False:
            return 0
        
    #if it made it through the loop, then there were no conflicts
    return 1


def all_after_time(this_week, args):
    """ iterates through courses in the schedule to make sure
     none are after a specific time
     args should be [course, timeslot]   
     Timeslot should be a time object:  time(12, 0)
     """
    hold = False
    args = args[0]  # args is read in as a tuple like: ([args],)
    for c in this_week.schedule.courses:
        hold = this_week.find_course(c)[0].start_time < args[1]
        if hold == False:
            return 0
    #if it made it through the loop, then there were no conflicts
    return 1


def course_before_time(this_week, args):
    # find the course and check that its time is before the constraining slot
    # args should be (<course>, <timeslot>)
    hold = False
    args = args[0]  # args is read in as a tuple like: ([args],)
    hold = this_week.find_course(args[0])[0].start_time < args[1]
    return 1 if hold else 0

def course_after_time(this_week, args):
    # find the course and check that its time is after the constraining slot
    # args should be (<course>, <timeslot>)
    hold = False
    args = args[0]  # args is read in as a tuple like: ([args],)
    hold = this_week.find_course(args[0])[0].start_time > args[1]
    return 1 if hold else 0
