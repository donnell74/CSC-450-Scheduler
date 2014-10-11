class Course:
    def __init__(self, code, credit, instructor):
        self.code = code
        self.credit = credit
        self.instructor = instructor

    def __eq__(self, other):
        if other == None:
            return False

        return self.code == other.code and \
               self.credit == other.credit

    def __str__(self):
        return str(self.code) + " " + str(self.credit) + " " + str(self.instructor)