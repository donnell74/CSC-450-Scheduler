from Tkinter import *

class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def add_instructor_constraint(self):
        pass
    
    def time(self):
        pass
    
    def location(self):
        pass
        
    def add_course_constraint(self):
        pass

    def createWidgets(self):
        
        self.button_course = Button(self, text="add course constraint", command=self.add_course_constraint)
        self.button_course.pack({"side": "left"})

        self.button_instructor = Button(self, text="add instructor constraint", command=self.add_instructor_constraint)
        self.button_instructor.pack({"side": "left"})
        
        self.button_time = Button(self, text="time", command=self.time)
        self.button_time.pack({"side": "left"})
        
        self.button_location = Button(self, text="location", command=self.location)
        self.button_location.pack({"side": "left"})
        
        var1 = StringVar(self)
        var1.set("one") # initial value
        self.option1 = OptionMenu(self, var1, "one", "two", "three", "four")
        self.option1.pack({"side": "left"})

        var2 = StringVar(self)
        var2.set("one") # initial value
        self.option2 = OptionMenu(self, var2, "one", "two", "three", "four")
        self.option2.pack({"side": "left"})

        message1 = Label(self, text="Course code")
        message1.pack({"side": "left"})

        message2 = Label(self, text="Instructor Name")
        message2.pack({"side": "left"})
        
        

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()

# from Tkinter import *
# 
# # the constructor syntax is:
# # OptionMenu(master, variable, *values)
# 
# OPTIONS = [
#     "egg",
#     "bunny",
#     "chicken"
# ]
# 
# master = Tk()
# 
# variable = StringVar(master)
# variable.set(OPTIONS[0]) # default value
# 
# w = apply(OptionMenu, (master, variable) + tuple(OPTIONS))
# w.pack()
# 
# mainloop()