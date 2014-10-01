class Course:
    def __init__(self, code, credit):
        self.code = code
        self.credit = credit

    def __eq__(self, other):
        if other == None:
            return False

        return self.code == other.code and \
               self.credit == other.credit

    def __str__(self):
        return self.code

