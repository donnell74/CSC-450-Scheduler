import structures

class Section:
    def __init__(self, course, time_slots):
        """Creates a course-like object specific to a week, with all the details of the week
           NOTE: all attributes are shallow copies of structure objects
           Assumes time_slots have at least 1 valid, filled in time slot
           IN: course object, list of time slots for course object
           OUT: Section object"""
        self.course = course
        #List of time slots
        self.time_slots = time_slots
        #Should always just be one
        self.room = time_slots[0].room
        self.instructor = time_slots[0].instructor
        self.week = time_slots[0].room.day.week
        #Multiple
        self.days = []

        self.update_from_slots()
 
    def update_from_slots(self):
        """Updates attributes based on time slots"""
        for each_slot in self.time_slots:
            self.days.append(each_slot.room.day)

    def __str__(self):
        return self.course.code
