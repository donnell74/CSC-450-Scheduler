        
class Course(object):
        
    def __init__(self, subject,
                 number, title):
        self.subject = subject
        self.number = number
        self.title = title
	
    def __str__(self):
        msg = 'Course: ' + self.code + \
              '\nName: ' + self.name + \
              '\nTime: ' + self.time + \
              '\nDays: ' + self.days + \
              '\nRoom: ' + self.room + \
              '\nLoc: ' + self.loc
        return msg
    def conflict(self, time,
                 days, room):
        if self.time == time and \
            self.days == days and \
            self.room == room:
                conflict = True
    def is_conflict(self):
        return self.conflict

	
            
soft_eng = Course('460', 'software engineering', '12:15pm', 'mwf', '305', 'cheek')
comp_net = Course('565', 'computer networking', '10:15pm', 'tr', '313', 'cheek')
print soft_eng
