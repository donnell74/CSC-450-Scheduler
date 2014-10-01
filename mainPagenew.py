import sys
from Tkinter import *
from guiClasses import *


# Define click functions
def click_home():
    top_label_text.set("Home Screen")
    return

def click_constraint():
    top_label_text.set("Constraint Screen")
    return

def click_view():
    top_label_text.set("View Screen")
    return

def click_misc():
    top_label_text.set("Misc Screen")
    return

def click_run():
    # run the scheduler
    top_label_text.set("Scheduler should be running...")
    return

def add_course_con():
    top_label_text.set("course constraint")
    return

def add_instructor_con():
    top_label_text.set("Instructor constraint")
    return



main_window = Tk()

window_width = 850
window_height = 600
screen_x_pos = (main_window.winfo_screenwidth() / 2) - (window_width / 2)
screen_y_pos = (main_window.winfo_screenheight() / 2) - (window_height / 2)

main_window.geometry(str(window_width) + 'x' + str(window_height) +\
                    '+' + str(screen_x_pos) + '+' + str(screen_y_pos))

# Next two lines are using guiClasses.py and TopLevel for sub-windows
#main = MainWindow(main_window)
#main.pack()

# Following section places everything on one window

main_window.title('CSC Scheduler')

top_label_text = StringVar()
top_label_text.set("You have just begun!")
top_label = Label(main_window, textvariable = top_label_text)
top_label.grid(row = 0, column = 2)

home_button = Button(main_window, text = "Home", width = 15, height = 5, command = click_home)
home_button.grid(row = 0, column = 0)

constraint_button = Button(main_window, text = "Constraint", width = 15, height = 5, command = click_constraint)
constraint_button.grid(row = 1, column = 0)

view_button = Button(main_window, text = "View", width = 15, height = 5, command = click_view)
view_button.grid(row = 2, column = 0)

misc_button = Button(main_window, text = "...", width = 15, height = 5, command = click_misc)
misc_button.grid(row = 3, column = 0)

run_button = Button(main_window, text = "RUN", width = 15, height = 10, bg = "green", command = click_run)
run_button.grid(row = 4, column = 0)

add_course_con =Button(main_window, text = "add course constraint", width =15, height =5, command = add_course_con)
add_course_con.grid(row = 1, column = 1)

add_instructor_con =Button(main_window, text = "add instructor constraint", width =15, height =5, command = add_instructor_con )
add_instructor_con.grid(row = 1, column = 27)



main_window.mainloop()   # NEED FOR MAC OSX AND WINDOWS

