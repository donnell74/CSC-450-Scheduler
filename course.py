
import datetime

#   The datetime module is military time (24 hour clock).
#
#   24 hour     12 hour
#   ----------------------
#   00:00       12:00 a.m (midnight: start of day)
#   05:00       5:00 a.m
#   12:00       12:00 p.m (noon)
#   17:00       5:00 p.m
#   24:00       24:00 p.m (midnight: end of day)
#
#   EXAMPLE:
#
#   t1 = datetime.timedelta(hours=17, minutes=30)   # t1 represents 5:30 p.m
#   t2 = datetime.timedelta(hours=14, minutes=30)   # t2 represents 2:30 p.m
#
#   print t1            output: 17:30:00
#   print (t1 - t2)     output: 3:00:00

class Course(object):
    """Define a course.

    Course Parameters:
    -------------------------------------------------
    PARAMETERS      TYPE        Potential Arguments
    
    subject         string      'csc', 'phy'
    code            string      '365', '450'
    section         string      '1', '2', '3'
    title           string      'software engineering'
    days            string      'mwf', 'tr', 'mtwrf'
    startTime       datetime    datetime.timedelta(hours=10, minutes=30)
    endTime         datetime    datetime.timedelta(hours=11, minutes=30)  
    instructor      string      'Eric D Shade (P)'
    location        string      'cheek'
    room            string      '308'
    """
    
    def __init__(self, subject, code,
                 section, title, days,
                 startTime, endTime, instructor,
                 room, location):
        """Initialize a course."""
        self.subject = subject
        self.code = code
        self.section = section
        self.title = title
        self.days = days
        self.startTime = startTime      # The time a course begins.
        self.endTime = endTime          # The time a course end.
        self.instructor = instructor
        self.room = room
        self.location = location
    def __str__(self):
        """Print the course information to console."""
        msg = "subject: " + self.subject + \
              "\ncode: " + self.code + \
              "\nsection: " + self.section + \
              "\ntitle: " + self.title + \
              "\ndays: " + self.days + \
              "\nstartTime: " + str(self.startTime) + \
              "\nendTime: " + str(self.endTime) + \
              "\ninstructor: " + self.instructor + \
              "\nroom: " + self.room + \
              "\nlocation: " + self.location
        return msg
    def time_conflict(self, other, time_constraint):
        """Return true if there is a time conflict between
        two courses.

        The parameter, other, is a course object.
        
        The parameter, time_constraint,
        is of the data type: datetime.timedelta(hour=int).
        """
        # if self and other are on similar days,
        # then check for a time conflict.
        if self.days_conflict(other):
            tmax = max(self.startTime, other.startTime)
            tmin = min(self.endTime, other.endTime)
            return ((tmax - tmin) < time_constraint)
        return False
    def days_conflict(self, other):
        """Return true if self and other
        have class on similar days."""
        d1 = len(self.days)
        d2 = len(other.days)
        if (d1 == d2):
            for i in xrange(d1):
                if (self.days[i] in other.days):
                    return True
        elif (d1 > d2):
            for i in xrange(d1):
                if (self.days[i] in other.days):
                    return True
        else:
            for i in xrange(d2):
                if (other.days[i] in self.days):
                    return True
        return False


def main():
    c1 = Course("CSC", "450", "1", "software engineering",
               "mwf", datetime.timedelta(hours=11, minutes=15),
                datetime.timedelta(hours=12, minutes=5),
               "Eric D Shade (P)", "308", "cheek")
    print c1, "\n\n"
    
    c2 = Course("CSC", "365", "1", "Internet Programming",
        "tr", datetime.timedelta(hours=9, minutes=5),
        datetime.timedelta(hours=9, minutes=55),
        "Jamil M Saquer (P)", "0001", "TEMP")
    print c2 , "\n\n"

    # Check if c1 and c2 times conflict.
    time_constraint = datetime.timedelta(hours=2)
    print c1.time_conflict(c2, time_constraint)    # Returns false 
    
main()
