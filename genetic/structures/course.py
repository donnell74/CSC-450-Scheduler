class Course:
    """ Represents a single course """

    def __init__(self, code, credit, instructor, capacity,
                 needs_computers, prescheduled_time=None,
                 is_prescheduled=False, is_lab=False):

        self.code = code
        self.credit = credit
        self.instructor = instructor
        self.capacity = capacity
        self.needs_computers = needs_computers
        self.is_prescheduled = is_prescheduled
        self.prescheduled_time = prescheduled_time
        self.absolute_course = self.get_absolute_course_code()
        self.is_lab = is_lab

    def get_absolute_course_code(self):
        """
        Returns a joined string of the absolute course code
            E.g.: CSC 130 001 -> CSC130; CSC 450 -> CSC450
        IN: split course code string
        OUT: absolute course code string
        """
        #todo: error if invalid code structure (less than 2 parts)
        code = self.code
        two_part_code = "".join(code.split(' ')[:2])
        return two_part_code

    def __eq__(self, other):
        if other == None:
            return False

        return self.code == other.code and self.credit == other.credit

    def __str__(self):
        return self.code
