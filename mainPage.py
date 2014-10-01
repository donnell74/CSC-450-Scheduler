import sys
from Tkinter import *
from guiClasses import *


# Define click functions
def click_home():
    top_label_text.set("Home Screen")
    content_frame.delete(ALL)
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
##main = MainWindow(main_window)
##main.pack()

# Following section places everything on one windowFO301028

main_window.title('CSC Scheduler')

top_label_text = StringVar()
top_label_text.set("You have just begun!")

# MENU SECTION
menu_frame = Frame(main_window, bg = 'red')
menu_frame.grid(row = 0, column = 0, rowspan = 6, columnspan = 2)

# MENU BUTTONS
home_button = Button(menu_frame, text = "Home", width = 15, height = 5, command = click_home)
home_button.pack()

constraint_button = Button(menu_frame, text = "Constraint", width = 15, height = 5, command = click_constraint)
constraint_button.pack()

view_button = Button(menu_frame, text = "View", width = 15, height = 5, command = click_view)
view_button.pack()

misc_button = Button(menu_frame, text = "...", width = 15, height = 5, command = click_misc)
misc_button.pack()

run_button = Button(menu_frame, text = "RUN", width = 15, height = 10, bg = "green", command = click_run)
run_button.pack()


# CONTENT SECTION
content_frame = Canvas(main_window)
content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)

top_label = Label(content_frame, textvariable = top_label_text)
top_label.pack(side = TOP)

add_course_con = Button(content_frame, text = "add course constraint", width =15, height =5, command = add_course_con)
add_course_con.pack(side = LEFT, padx = 2, pady = 2)

add_instructor_con = Button(content_frame, text = "add instructor constraint", width =15, height =5, command = add_instructor_con )
add_instructor_con.pack(side = LEFT, padx = 5, pady = 2)



main_window.mainloop()   # NEED FOR MAC OSX AND WINDOWS

